from PySide6.QtGui import QBrush, QColor, QFont, QFontMetrics, QLinearGradient, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsLineItem, QGraphicsPathItem, QGraphicsRectItem, QGraphicsTextItem
from PySide6.QtCore import Qt
from datetime import timedelta
from ui.drag_drop import attach_char_drag

class TimelineRenderer:
    """Handles all drawing for timeline"""
    def __init__(self, timeline_controller):
        self.timeline_controller = timeline_controller
        self.scene = timeline_controller.scene
        self.main_controller = timeline_controller.main_controller
        self.DAY_WIDTH = timeline_controller.DAY_WIDTH
        self.LANE_HEIGHT = timeline_controller.LANE_HEIGHT
        self.LEFT_MARGIN = timeline_controller.LEFT_MARGIN
        self.TOP_MARGIN = timeline_controller.TOP_MARGIN

    def draw_place_lanes(self, lane_items, lane_tops, lane_heights, lane_colors, day_count, start_index=0):
        """Draws the background and labels for each place"""
        lane_items = list(lane_items)
        scene_width = self.scene.sceneRect().width()
        width = max(day_count * self.DAY_WIDTH + 200, scene_width - (self.LEFT_MARGIN - 20))

        for offset in range(len(lane_items)):
            lane_id, label = lane_items[offset]
            lane_index = start_index + offset
            lane_height = lane_heights[start_index + offset]
            y = lane_tops.get(lane_id, self.TOP_MARGIN + lane_index * self.LANE_HEIGHT)

            dark_mode = getattr(self.main_controller, "dark_mode_enabled", False)
            if dark_mode:
                background_color = QColor("#232323")
                label_box_color = QColor("#333333")
                text_color = QColor("#cccccc")
                baseline_color = QColor("#444444")
            else:
                base_lane_color = lane_colors.get(lane_id, QColor("#dfe3eb"))
                lane_color = QColor(base_lane_color)
                if not lane_color.isValid():
                    lane_color = QColor("#dfe3eb")
                background_color = QColor("#f5f5f7") if lane_index % 2 == 0 else QColor("#eeeeef")
                label_box_color = None
                text_color = QColor("#333333")
                baseline_color = QColor("#bbbbbb")

            rect = QGraphicsRectItem(self.LEFT_MARGIN - 20, y, width, lane_height)
            rect.setBrush(QBrush(background_color))
            rect.setPen(QPen(QColor("#444444") if dark_mode else QColor("#dddddd")))
            rect.setData(0, {'kind': 'place', 'id': lane_id})
            self.scene.addItem(rect)

            label_box_width = max(120, self.LEFT_MARGIN - 60)
            label_box_height = 34
            label_box_x = 20
            label_box_y = y + 12
            label_box = QGraphicsRectItem(label_box_x, label_box_y, label_box_width, label_box_height)
            if label_box_color is None:
                label_box.setBrush(Qt.NoBrush)
                box_pen_color = QColor("#555555") if dark_mode else QColor("#cccccc")
                box_pen = QPen(box_pen_color)
            else:
                label_box.setBrush(QBrush(label_box_color))
                box_pen = QPen(label_box_color.darker(140))
            box_pen.setWidthF(1.2)
            label_box.setPen(box_pen)
            if lane_id != "__NO_PLACE__":
                label_box.setData(0, {'kind': 'place', 'id': lane_id, 'role': 'label'})
            else:
                label_box.setData(0, {'kind': 'place', 'id': lane_id})
            label_box.setZValue(1)
            self.scene.addItem(label_box)

            font = QFont("Arial", 12, QFont.Bold)
            metrics = QFontMetrics(font)
            available_width = int(max(0, label_box_width - 20))
            display_text = metrics.elidedText(label or "", Qt.ElideRight, available_width)

            text_item = QGraphicsTextItem(display_text)
            text_item.setFont(font)
            text_item.setDefaultTextColor(text_color)
            text_item.setToolTip(label or "")
            text_rect = text_item.boundingRect()
            text_x = label_box_x + 12
            text_y = label_box_y + max(2, (label_box_height - text_rect.height()) / 2)
            text_item.setPos(text_x, text_y)
            text_item.setZValue(2)
            if lane_id != "__NO_PLACE__":
                text_item.setData(0, {'kind': 'place', 'id': lane_id, 'role': 'label'})
            else:
                text_item.setData(0, {'kind': 'place', 'id': lane_id})
            self.scene.addItem(text_item)

            baseline = QGraphicsLineItem(self.LEFT_MARGIN - 20, y + lane_height, self.LEFT_MARGIN + width, y + lane_height)
            baseline.setPen(QPen(baseline_color))
            self.scene.addItem(baseline)

    def draw_day_grid(self, min_date, day_count, total_height, axis_labels=None):
        """Draw the vertical grid lines and day names on the timeline."""
        dark_mode = getattr(self.main_controller, "dark_mode_enabled", False)
        grid_color = QColor("#555555") if dark_mode else QColor("#dddddd")
        text_color = QColor("#cccccc") if dark_mode else QColor("#666666")

        for i in range(day_count + 1):
            x = self.LEFT_MARGIN + i * self.DAY_WIDTH
            if i == 0:
                line = QGraphicsLineItem(x - 20, self.TOP_MARGIN - 30, x - 20, total_height)
            else:
                line = QGraphicsLineItem(x, self.TOP_MARGIN - 30, x, total_height)
            line.setPen(QPen(grid_color))
            self.scene.addItem(line)

            if i < day_count:
                if axis_labels is not None:
                    if i < len(axis_labels):
                        day_text = axis_labels[i]
                    else:
                        day_text = "Day " + str(i + 1)
                else:
                    current_date = min_date + timedelta(days=i)
                    day_text = current_date.strftime("%Y-%m-%d")

                text_item = QGraphicsTextItem(day_text)
                text_item.setDefaultTextColor(text_color)
                font = QFont("Arial", 10)
                text_item.setFont(font)
                text_rect = text_item.boundingRect()
                text_x = x + (self.DAY_WIDTH - text_rect.width()) / 2
                text_y = self.TOP_MARGIN - 28
                text_item.setPos(text_x, text_y)
                self.scene.addItem(text_item)

    def draw_participants(self, event, participants, x, y, width, height, event_color):
        """Draws small colored boxes for each participant in event"""
        participant_limit = 10
        participants_to_show = []
        for i in range(min(participant_limit, len(participants))):
            participants_to_show.append(participants[i])
        if len(participants) > participant_limit:
            extra = len(participants) - participant_limit
            participants_to_show.append("+" + str(extra) + " more")

        if len(participants_to_show) > 0:
            char_size = min(16, max(8, int(height // max(len(participants_to_show), 1) - 2)))
        else:
            char_size = 8
        padding = 2
        start_y = y + padding

        for i in range(len(participants_to_show)):
            p = participants_to_show[i]
            char_y = start_y + i * (char_size + padding)
            if char_y + char_size > y + height:
                break

            if isinstance(p, str) and p.startswith("+"):
                text_item = QGraphicsTextItem(p)
                text_item.setFont(QFont("Arial", max(6, char_size - 2)))
                text_item.setDefaultTextColor(QColor("#666666"))
                text_item.setPos(x + width + 4, char_y)
                text_item.setData(0, {'kind': 'event_extra', 'event_id': event.id})
                self.scene.addItem(text_item)
                continue

            char_color = self.timeline_controller.color_manager.safe_char_color(p)
            char_rect = QGraphicsRectItem(x + width + 4, char_y, char_size, char_size)
            char_rect.setBrush(QBrush(char_color))
            char_rect.setPen(QPen(char_color.darker(120)))
            char_rect.setData(0, {'kind': 'character', 'id': p.id, 'name': p.name})
            self.scene.addItem(char_rect)

            attach_char_drag(char_rect, p.id, p.name)

            char_label_color = self.timeline_controller.color_manager.char_label_color(char_color, char_color)
            label_text = QGraphicsTextItem(p.name[:8] + ("..." if len(p.name) > 8 else ""))
            label_text.setFont(QFont("Arial", max(6, char_size - 2)))
            label_text.setDefaultTextColor(char_label_color)
            label_text.setPos(x + width + char_size + 8, char_y)
            label_text.setData(0, {'kind': 'character', 'id': p.id, 'name': p.name})
            self.scene.addItem(label_text)

    def draw_lane_characters(self, lane_items, lane_map, lane_tops, lane_heights):
        """Draws characters in their places"""
        characters_map = self.timeline_controller._characters_map
        for character in characters_map.values():
            if hasattr(character, 'associated_places'):
                character_places = character.associated_places
            else:
                character_places = []
            if not character_places:
                continue
            char_color = self.timeline_controller.color_manager.safe_char_color(character)
            for place_id in character_places:
                if place_id not in lane_map:
                    continue
                lane_index = lane_map[place_id]
                y = lane_tops.get(place_id, self.TOP_MARGIN + lane_index * self.LANE_HEIGHT)
                lane_height = lane_heights[lane_index]
                # Count how many characters before this one in the same lane
                count = 0
                for c in characters_map.values():
                    if hasattr(c, 'associated_places') and place_id in c.associated_places and c.id < character.id:
                        count += 1
                char_x = 30 + count * 20
                char_y = y + lane_height - 30
                char_size = 16
                char_rect = QGraphicsRectItem(char_x, char_y, char_size, char_size)
                char_rect.setBrush(QBrush(char_color))
                char_rect.setPen(QPen(char_color.darker(120)))
                char_rect.setData(0, {'kind': 'character', 'id': character.id, 'name': character.name})
                self.scene.addItem(char_rect)
                attach_char_drag(char_rect, character.id, character.name)

    def draw_event_block(self, event, x, y, width, height, event_color, participants):
        """Draws a block for an event, with title and participants"""
        dark_mode = getattr(self.main_controller, "dark_mode_enabled", False)
        rect = QGraphicsRectItem(x, y, width, height)
        if not dark_mode:
            gradient = QLinearGradient(0, 0, 0, height)
            gradient.setColorAt(0, event_color.lighter(110))
            gradient.setColorAt(1, event_color.darker(110))
            rect.setBrush(QBrush(gradient))
        else:
            rect.setBrush(QBrush(event_color))
        rect.setPen(QPen(event_color.darker(140), 1.5))
        rect.setData(0, {'kind': 'event', 'id': event.id})
        self.scene.addItem(rect)
        title_text = event.name[:20] + ("..." if len(event.name) > 20 else "")
        text_item = QGraphicsTextItem(title_text)
        text_item.setFont(QFont("Arial", 10, QFont.Bold))
        text_color = self.timeline_controller.color_manager.ensure_readable(QColor("#000000"), event_color, 4.5)
        text_item.setDefaultTextColor(text_color)
        text_item.setPos(x + 5, y + 5)
        text_item.setData(0, {'kind': 'event', 'id': event.id})
        self.scene.addItem(text_item)
        if participants:
            self.draw_participants(event, participants, x, y, width, height, event_color)

    def draw_char_paths(self, char_points, opacity=0.7):
        """Draws dashed paths for characters across events"""
        for char_id in char_points:
            points = char_points[char_id]
            if len(points) < 2:
                continue
            character = self.timeline_controller._characters_map.get(char_id)
            if not character:
                continue
            char_color = self.timeline_controller.color_manager.safe_char_color(character)
            path = QPainterPath()
            path.moveTo(points[0][0], points[0][1])
            for i in range(1, len(points)):
                path.lineTo(points[i][0], points[i][1])
            path_item = QGraphicsPathItem(path)
            pen = QPen(char_color, 2, Qt.DashLine)
            pen.setCapStyle(Qt.RoundCap)
            path_item.setPen(pen)
            path_item.setOpacity(opacity)
            path_item.setData(0, {'kind': 'character_path', 'id': char_id})
            path_item.setZValue(-1)
            self.scene.addItem(path_item)
