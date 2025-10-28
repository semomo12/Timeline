from typing import Any, Dict, List, Set, Tuple
from PySide6.QtGui import QColor, QBrush, QPen, QFontMetrics, QFont, QPainterPath
from PySide6.QtWidgets import QGraphicsRectItem,QGraphicsTextItem,QGraphicsDropShadowEffect,QGraphicsBlurEffect,QGraphicsPathItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from ui.drag_drop import attach_char_drag

def draw_participants(
    controller,
    event,
    participants: List[Any],
    x: float,
    y: float,
    width: float,
    height: float,
    content_top: float,
    char_points: Dict[str, List[Tuple[float, float]]],
    char_bounds: Dict[str, List[Tuple[float, float, float, float]]],
    characters_with_blocks: Set[str],
):
    """Render participant blocks within event."""
    if not participants:
        return
    color_manager = controller.color_manager
    scene = controller.scene
    filtered = controller._filtered_characters

    zone_top = max(content_top + 10.0, y + 30.0)
    zone_bottom = y + height - 12.0
    block_width_available = max(32.0, width - 16.0)
    measurements = controller._measure_participant_blocks(participants, block_width_available)
    (
        measurements,
        font,
        _metrics,
        text_width,
        padding_x,
        padding_y,
        block_spacing,
    ) = measurements
    needed_height = sum(h for h, _ in measurements)
    if len(measurements) > 1:
        needed_height += block_spacing * (len(measurements) - 1)
    if needed_height > (zone_bottom - zone_top):
        zone_top = max(y + 24.0, zone_bottom - needed_height)

    block_width = block_width_available
    bounds = (x + 4.0, x + width - 4.0, y + 4.0, y + height - 4.0)
    tooltip_suffix = f"Event: {event.name}"
    current_top = zone_top
    last_index = len(measurements) - 1
    for idx, (character, (block_height, _)) in enumerate(zip(participants, measurements)):
        color = color_manager.safe_char_color(QColor(character.color))
        background_color = QColor(color).lighter(170)
        block_left = x + 8.0
        is_character_focused = character.id in filtered
        if filtered:
            if is_character_focused:
                color = color.lighter(140)
                pen_width = 2.5
                pen_color = QColor("#ff4500")
                opacity = 1.0
                blur_radius = 0.0
                text_color = QColor("#000000")
            else:
                color = color.darker(220)
                pen_width = 1.2
                pen_color = color.darker(140)
                opacity = 0.25
                blur_radius = 0.0
                text_color = QColor("#999999")
        else:
            pen_width = 1.2
            pen_color = color.darker(140)
            opacity = 1.0
            blur_radius = 0.0
            text_color = color_manager.char_label_color(color, background_color)

        rect = QGraphicsRectItem(block_left, current_top, block_width, block_height)
        rect.setBrush(QBrush(background_color))
        border_pen = QPen(pen_color)
        border_pen.setWidthF(pen_width)
        rect.setPen(border_pen)
        rect.setData(0, {'kind': 'character', 'id': character.id, 'character': character, 'event': event})
        rect.setToolTip(f"{character.name}\n{tooltip_suffix}")
        rect.setOpacity(opacity)
        rect.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        rect.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        rect.setCursor(QCursor(Qt.OpenHandCursor))

        def _refresh_after_drag():
            controller._preserve_next_view_position = True
            controller.navigation_manager.refresh_all()
        attach_char_drag(
            rect,
            character=character,
            source_event=event,
            get_drop_target=controller._get_character_drop_target_event,
            validate_move=controller._validate_move,
            move_to_event=controller.character_manager.move_to_event_now,
            move_within_event=controller.character_manager.reposition_within_event_now,
            refresh=_refresh_after_drag,
        )
        if filtered and is_character_focused:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20.0)
            shadow.setColor(QColor(255, 69, 0, 140))
            shadow.setOffset(2, 4)
            rect.setGraphicsEffect(shadow)
        elif blur_radius > 0:
            blur_effect = QGraphicsBlurEffect()
            blur_effect.setBlurRadius(blur_radius)
            rect.setGraphicsEffect(blur_effect)

        scene.addItem(rect)
        char_metrics = QFontMetrics(font)
        available_char_width = int(max(0.0, text_width))
        elided_char_name = (
            char_metrics.elidedText(character.name, Qt.ElideRight, available_char_width)
            if available_char_width > 0 else character.name
        )
        label = QGraphicsTextItem(elided_char_name)
        label.setFont(font)
        label.setDefaultTextColor(text_color)
        text_x = block_left + padding_x
        label_rect = label.boundingRect()
        text_y = current_top + max(0.0, (block_height - label_rect.height()) / 2.0)
        label.setPos(text_x, text_y)
        label.setData(0, {'kind': 'character', 'id': character.id})
        label.setToolTip(f"{character.name}\n{tooltip_suffix}")
        label.setOpacity(opacity)
        if filtered and is_character_focused:
            text_shadow = QGraphicsDropShadowEffect()
            text_shadow.setBlurRadius(6.0)
            text_shadow.setColor(QColor(255, 69, 0, 70))
            text_shadow.setOffset(1, 1)
            label.setGraphicsEffect(text_shadow)
        elif blur_radius > 0:
            text_blur_effect = QGraphicsBlurEffect()
            text_blur_effect.setBlurRadius(blur_radius)
            label.setGraphicsEffect(text_blur_effect)
        scene.addItem(label)
        center_x = block_left + block_width / 2.0
        center_y = current_top + block_height / 2.0
        char_points[character.id].append((center_x, center_y))
        char_bounds[character.id].append(bounds)
        characters_with_blocks.add(character.id)
        if idx != last_index:
            current_top += block_height + block_spacing


def draw_char_paths(
    controller,
    char_points: Dict[str, List[Tuple[float, float]]],
    char_bounds: Dict[str, List[Tuple[float, float, float, float]]],
    characters: Dict[str, Any],
    characters_with_blocks: Set[str],
):
    """Show connecting lines between all of a character’s timeline events."""
    scene = controller.scene
    color_manager = controller.color_manager
    filtered = controller._filtered_characters
    for char_id, points in char_points.items():
        character = characters.get(char_id)
        if not character or not points:
            continue
        has_internal_block = char_id in characters_with_blocks
        points.sort(key=lambda item: item[0])
        color = color_manager.safe_char_color(QColor(character.color))

        is_character_focused = char_id in filtered
        if filtered:
            if is_character_focused:
                color = color.lighter(130)
                path_width = 4
                opacity = 1.0
                blur_radius = 0.0
                text_color = QColor("#000000")
            else:
                color = color.darker(200)
                path_width = 2
                opacity = 0.25
                blur_radius = 0.0
                text_color = QColor("#999999")
        else:
            path_width = 3
            opacity = 1.0
            blur_radius = 0.0
            bg_brush = scene.backgroundBrush()
            if hasattr(bg_brush, "style") and bg_brush.style() != Qt.NoBrush:
                background_color = bg_brush.color()
            else:
                dark_mode = getattr(controller.main_controller, "dark_mode_enabled", False)
                background_color = QColor("#232323") if dark_mode else QColor("#ffffff")
            text_color = color_manager.char_label_color(color, background_color)

        if len(points) > 1:
            path = QPainterPath()
            x0, y0 = points[0]
            path.moveTo(x0, y0)
            for idx in range(1, len(points)):
                x_prev, y_prev = points[idx - 1]
                x_curr, y_curr = points[idx]
                mid_x = (x_prev + x_curr) / 2.0
                path.cubicTo(mid_x, y_prev, mid_x, y_curr, x_curr, y_curr)
            pen = QPen(color, path_width)
            pen.setCosmetic(True)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            path_item = QGraphicsPathItem(path)
            path_item.setPen(pen)
            path_item.setZValue(-1)
            path_item.setOpacity(opacity)
            if blur_radius > 0:
                blur_effect = QGraphicsBlurEffect()
                blur_effect.setBlurRadius(blur_radius)
                path_item.setGraphicsEffect(blur_effect)
            scene.addItem(path_item)
        if has_internal_block:
            continue
        font = QFont("Arial", 9, QFont.Bold)
        label = QGraphicsTextItem()
        label.setFont(font)
        label.setDefaultTextColor(text_color)

        bounds_list = char_bounds.get(char_id)
        if bounds_list and len(bounds_list) > 0:
            left = min(b[0] for b in bounds_list)
            right = max(b[1] for b in bounds_list)
            top = min(b[2] for b in bounds_list)
            bottom = max(b[3] for b in bounds_list)
        else:
            left = controller.LEFT_MARGIN
            right = controller.scene.sceneRect().right() - 6
            top = controller.TOP_MARGIN
            bottom = top + controller.LANE_HEIGHT - controller.LANE_PADDING

        max_width = max(40, right - left)
        metrics = QFontMetrics(font)
        short_name = metrics.elidedText(character.name, Qt.ElideRight, int(max_width))
        label.setPlainText(short_name)

        label_width = label.boundingRect().width()
        label_x = left + (max_width - label_width) / 2
        label_y = bottom + 8
        label.setPos(label_x, label_y)
        label.setData(0, {'kind': 'character', 'id': character.id})
        scene.addItem(label)
