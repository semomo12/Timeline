from PySide6.QtGui import QBrush, QColor
from PySide6.QtCore import Qt
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Set, Tuple
from core.logic.ui.drag_drop_manager import TimelineDragDropManager
from core.data.timeline_data import TimelineHandler
from core.logic.objects.character_controller import CharacterController
from core.logic.objects.event_controller import EventController
from core.data.data_manager import TimelineDataManager
from core.utils.validation_manager import TimelineValidationManager
from ui.scene import TimelineScene
from ui.graphics.color import TimelineColorManager
from ui.graphics.render import TimelineRenderer
from ui.graphics.layout import TimelineLayoutManager
from ui.info_dialogs import TimelineInfoDialogs
from ui.click_handler import TimelineClickHandler
from ui.navigation import NavigationController
from ui.graphics.drawing import draw_event_block
from ui.graphics.participants import draw_participants as render_event_participants, draw_char_paths as render_character_paths


class TimelineController:
    """Controller for timeline view."""

    @property
    def project(self):
        return self.main_controller.project

    DAY_WIDTH = 120
    LANE_HEIGHT = 120
    LEFT_MARGIN = 180
    TOP_MARGIN = 80
    LANE_PADDING = 20

    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.scene = TimelineScene(self)
        self.color_manager = TimelineColorManager(self)
        self.data_processor = TimelineHandler(main_controller)
        self.renderer = TimelineRenderer(self)
        self.layout_manager = TimelineLayoutManager(self)
        self.drag_drop_manager = TimelineDragDropManager(self)
        self.info_dialogs = TimelineInfoDialogs(self)
        self.character_manager = CharacterController(self.main_controller)
        self.event_manager = EventController(self.main_controller)
        self.data_manager = TimelineDataManager(self)
        self.click_handler = TimelineClickHandler(self)
        self.navigation_manager = NavigationController(main_controller)
        self.validation_manager = TimelineValidationManager(self)

        view = getattr(self.main_controller, "viewTimeline", None)
        if view:
            view.setScene(self.scene)
            view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        else:
            print("Warning: viewTimeline not found")

        self.zoom_level = 1.0
        self.current_min_date = None
        self.current_day_count = 0
        self.current_mode = "calendar"
        self.current_lane_count = 0
        self._events_map = {}
        self._characters_map = {}
        self._places_map = {}
        self._filtered_characters = set()
        self._preserve_next_view_position = False

    def update_timeline(self):
        view = getattr(self.main_controller, "viewTimeline", None)
        if not view:
            return

        preserve_scroll = self._preserve_next_view_position
        saved_scroll = None
        saved_v_fraction = None
        if preserve_scroll:
            h_bar = view.horizontalScrollBar()
            v_bar = view.verticalScrollBar()

            if v_bar and v_bar.maximum() > 0:
                saved_v_fraction = v_bar.value() / v_bar.maximum()
            else:
                saved_v_fraction = 0.0
            saved_scroll = (
                h_bar.value() if h_bar else None,
                v_bar.value() if v_bar else None,
            )
        self._preserve_next_view_position = False

        self.scene.clear()

        dark_mode = getattr(self.main_controller, "dark_mode_enabled", False)
        bg_color = QColor("#232323") if dark_mode else QColor("#ffffff")
        self.scene.setBackgroundBrush(QBrush(bg_color))

        self.color_manager.clear_caches()

        mode = getattr(self.main_controller, "timeline_mode", "calendar")
        parsed_events = self._collect_events(mode)

        characters = {}
        for char in self.main_controller.project.characters:
            characters[char.id] = char
        places = {}
        for place in self.main_controller.project.places:
            places[place.id] = place
        events_map = {}
        for event in self.main_controller.project.events:
            events_map[event.id] = event

        self._characters_map = characters
        self._places_map = places
        self._events_map = events_map

        lane_items = self._build_lane_order(parsed_events, places)
        lane_map = {}
        for index, lane_info in enumerate(lane_items):
            lane_id, _lane_label = lane_info
            lane_map[lane_id] = index
        lane_colors = {}
        for lane_id, _lane_label in lane_items:
            lane_colors[lane_id] = self.color_manager.place_color(lane_id)
        characters_in_events = set()
        for parsed in parsed_events:
            event_obj = parsed.get('event')
            participants = getattr(event_obj, 'participants', [])
            for char_id in participants:
                characters_in_events.add(char_id)

        self.current_mode = mode
        self.current_lane_count = max(1, len(lane_items))
        self.current_min_date = None
        self.current_day_count = 0

        if not parsed_events:
            day_count = 10
            today = datetime.today()
            min_date = datetime(today.year, today.month, today.day)
            axis_labels = None
            if mode == "day_sequence":
                axis_labels = []
                for index in range(day_count):
                    axis_labels.append(f"Day {index + 1}")

            if not lane_items:
                lane_items = [("__NO_PLACE__", "No Place")]

            lane_colors = {}
            for lane_id, _lane_label in lane_items:
                lane_colors[lane_id] = self.color_manager.place_color(lane_id)
            lane_heights = []
            for _lane in lane_items:
                height_value = max(self.LANE_HEIGHT, 160.0)
                lane_heights.append(height_value)
            lane_height_map = {}
            for idx, lane_info in enumerate(lane_items):
                lane_id, _lane_label = lane_info
                lane_height_map[lane_id] = lane_heights[idx]
            lane_tops: Dict[str, float] = {}
            current_top = self.TOP_MARGIN
            for (lane_id, _), lane_height in zip(lane_items, lane_heights):
                lane_tops[lane_id] = current_top
                current_top += lane_height

            total_height = current_top + 120.0
            total_width = self.LEFT_MARGIN + day_count * self.DAY_WIDTH + 300

            width = total_width
            height = total_height
            viewport = view.viewport()
            if viewport:
                width = max(width, viewport.width() / max(self.zoom_level, 1e-3))
                height = max(height, viewport.height() / max(self.zoom_level, 1e-3))
            self.scene.setSceneRect(0, 0, width, height)

            self._draw_place_lanes(lane_items, lane_tops, lane_heights, lane_colors, day_count)
            self._draw_day_grid(min_date, day_count, total_height, axis_labels=axis_labels)

            self.current_min_date = min_date
            self.current_day_count = day_count
            if preserve_scroll and saved_scroll:
                h_bar = view.horizontalScrollBar()
                v_bar = view.verticalScrollBar()
                if h_bar and saved_scroll[0] is not None:
                    h_bar.setValue(saved_scroll[0])

                if v_bar and saved_v_fraction is not None and v_bar.maximum() > 0:
                    v_bar.setValue(int(saved_v_fraction * v_bar.maximum()))
            return

        axis_labels = None
        if mode == "day_sequence":
            sequence_values = []
            for item in parsed_events:
                start_value = item['sequence_start']
                end_value = item['sequence_end']
                if start_value is not None:
                    sequence_values.append(start_value)
                if end_value is not None:
                    sequence_values.append(end_value)
            if sequence_values:
                seq_min = min(sequence_values)
                seq_max = max(sequence_values)
            else:
                seq_min = 1
                seq_max = 1
            day_count = max(1, seq_max - seq_min + 1)
            axis_labels = []
            for offset in range(day_count):
                axis_labels.append(f"Day {seq_min + offset}")

            today = datetime.today()
            min_date = datetime(today.year, today.month, today.day)
            max_date = min_date + timedelta(days=day_count - 1)
        else:
            valid_dates = []
            for item in parsed_events:
                if item['start'] is not None:
                    valid_dates.append(item['start'])
                if item['end'] is not None:
                    valid_dates.append(item['end'])

            if not valid_dates:
                today = datetime.today()
                min_date = datetime(today.year, today.month, today.day)
                max_date = min_date
            else:
                min_date = min(valid_dates)
                max_date = max(valid_dates)
                if min_date > max_date:
                    min_date, max_date = max_date, min_date
            day_count = max(1, (max_date - min_date).days + 1)

        total_height = self.TOP_MARGIN + len(lane_items) * self.LANE_HEIGHT + 100
        total_width = self.LEFT_MARGIN + day_count * self.DAY_WIDTH + 300

        width = total_width
        height = total_height
        viewport = view.viewport()
        if viewport:
            width = max(width, viewport.width() / max(self.zoom_level, 1e-3))
            height = max(height, viewport.height() / max(self.zoom_level, 1e-3))
        self.scene.setSceneRect(0, 0, width, height)
        
        lane_labels = {lane_id: label for lane_id, label in lane_items}

        if mode == "day_sequence":
            parsed_events.sort(key=lambda item: (item['sequence_start'] or 0, item['event'].name.lower()))
        else:
            parsed_events.sort(key=lambda item: (item['start'], item['event'].name.lower()))

        events_to_draw: List[Dict[str, Any]] = []
        lane_event_map: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        for parsed in parsed_events:
            event = parsed['event']
            place_id = self._resolve_event_place(event, lane_map)
            if place_id not in lane_map:
                continue

            if mode == "day_sequence":
                start_offset = (parsed['sequence_start'] or 1) - 1  # Day 1 = offset 0
                end_offset = (parsed['sequence_end'] or parsed['sequence_start'] or 1) - 1
            else:
                start_offset = (parsed['start'] - min_date).days
                end_offset = max(start_offset, (parsed['end'] - min_date).days)

            duration_days = max(1, end_offset - start_offset + 1)

            participants: List[Any] = []
            seen_participant_ids: Set[str] = set()
            for c_id in event.participants:
                if c_id in characters and c_id not in seen_participant_ids:
                    participants.append(characters[c_id])
                    seen_participant_ids.add(c_id)

            info = {
                'parsed': parsed,
                'event': event,
                'lane_id': place_id,
                'lane_label': lane_labels.get(place_id, place_id),
                'start_offset': start_offset,
                'end_offset': end_offset,
                'duration_days': duration_days,
                'participants': participants,
                'participant_names': [character.name for character in participants],
                'is_point': parsed['is_point'],
                'place_color': lane_colors.get(place_id),
                'approx_width': max(self.DAY_WIDTH * 0.35, duration_days * self.DAY_WIDTH - 12),
            }
            events_to_draw.append(info)
            lane_event_map[place_id].append(info)

        for lane_id, lane_events in lane_event_map.items():
            self.layout_manager.assign_columns(lane_events)

        lane_heights, lane_tops, structural_height = self.layout_manager.lane_layout(lane_items, lane_event_map)
        lane_height_map = {lane_id: lane_heights[idx] for idx, (lane_id, _) in enumerate(lane_items)}

        total_width = self.LEFT_MARGIN + day_count * self.DAY_WIDTH + 300
        total_height = structural_height + 40.0

        width = total_width
        height = total_height
        viewport = view.viewport()
        if viewport:
            width = max(width, viewport.width() / max(self.zoom_level, 1e-3))
            height = max(height, viewport.height() / max(self.zoom_level, 1e-3))
        self.scene.setSceneRect(0, 0, width, height)

        self._draw_place_lanes(lane_items, lane_tops, lane_heights, lane_colors, day_count, start_index=0)
        self._draw_day_grid(min_date, day_count, structural_height, axis_labels=axis_labels)

        char_points: Dict[str, List[Tuple[float, float]]] = defaultdict(list)
        char_bounds: Dict[str, List[Tuple[float, float, float, float]]] = defaultdict(list)
        characters_with_event_blocks: Set[str] = set()

        roster_reserved = 56.0

        for info in events_to_draw:
            lane_id = info['lane_id']
            lane_top = lane_tops.get(lane_id, self.TOP_MARGIN)
            lane_height = lane_height_map.get(lane_id, self.LANE_HEIGHT)
            start_offset = info['start_offset']
            duration_days = info['duration_days']
            base_x = self.LEFT_MARGIN + start_offset * self.DAY_WIDTH + 6
            base_width = max(self.DAY_WIDTH * 0.35, duration_days * self.DAY_WIDTH - 12)
            width = base_width
            x = base_x
            if info['is_point']:
                point_width = self.DAY_WIDTH * 0.35
                width = min(width, point_width)
                x = self.LEFT_MARGIN + start_offset * self.DAY_WIDTH + (self.DAY_WIDTH - width) / 2
            approx_width = max(width, self.DAY_WIDTH * 0.35)

            column = info.get('column', 0)
            column_count = max(1, info.get('column_count', 1))
            available_height = max(48.0, lane_height - 2 * self.LANE_PADDING - roster_reserved)
            slot_height = available_height / column_count if column_count else available_height
            desired_height = self.layout_manager.event_height(info['participants'], approx_width)
            slot_height = max(slot_height, desired_height)
            height = max(36.0, desired_height)
            y = lane_top + self.LANE_PADDING + column * slot_height + (slot_height - height) / 2
            max_y = lane_top + lane_height - roster_reserved - height - 10.0
            y = min(y, max_y)

            content_top = draw_event_block(
                self.scene,
                info['event'],
                x,
                y,
                width,
                height,
                info['lane_label'],
                info['participant_names'],
                info.get('place_color'),
                self._filtered_characters,
            )

            participants = info['participants']
            if participants:
                self._draw_event_participants(
                    info['event'],
                    participants,
                    x,
                    y,
                    width,
                    height,
                    content_top,
                    char_points,
                    char_bounds,
                    characters_with_event_blocks,
                )

        self.current_min_date = min_date
        self.current_day_count = day_count

        self._draw_character_paths(char_points, char_bounds, characters, characters_with_event_blocks)
        if preserve_scroll and saved_scroll:
            h_bar = view.horizontalScrollBar()
            v_bar = view.verticalScrollBar()
            if h_bar and saved_scroll[0] is not None:
                h_bar.setValue(saved_scroll[0])
            if v_bar and saved_scroll[1] is not None:
                v_bar.setValue(saved_scroll[1])

    def zoom_in(self):
        if self.navigation_manager:
            self.navigation_manager.zoom_in_view()

    def zoom_out(self):
        if self.navigation_manager:
            self.navigation_manager.zoom_out_view()

    def _collect_events(self, mode):
        return self.data_manager.get_events(mode)

    def _parse_date(self, value):
        return self.data_manager.parse_date(value)

    def _extract_day_index(self, value):
        return self.data_manager.extract_day_index(value)

    def _build_lane_order(self, parsed_events, places):
        """Based on places and events"""
        return self.layout_manager.build_lane_order(parsed_events, places)

    def _draw_place_lanes(self, lane_items: Iterable[Tuple[str, str]], lane_tops: Dict[str, float],
                          lane_heights: List[float], lane_colors: Dict[str, QColor],
                          day_count: int, start_index: int = 0):
        """Draw place lanes"""
        return self.renderer.draw_place_lanes(lane_items, lane_tops, lane_heights, lane_colors, day_count, start_index)

    def _draw_day_grid(self, min_date, day_count, total_height, axis_labels= None):
        return self.renderer.draw_day_grid(min_date, day_count, total_height, axis_labels)

    def _draw_event_participants(self, event, participants: List[Any], x: float, y: float,
                                 width: float, height: float, content_top: float,
                                 char_points: Dict[str, List[Tuple[float, float]]],
                                 char_bounds: Dict[str, List[Tuple[float, float, float, float]]],
                                 characters_with_blocks: Set[str]):
        render_event_participants(
            self, event, participants, x, y, width, height, content_top,
            char_points, char_bounds, characters_with_blocks
        )

    def _draw_character_paths(self, char_points: Dict[str, List[Tuple[float, float]]],
                              char_bounds: Dict[str, List[Tuple[float, float, float, float]]],
                              characters: Dict[str, Any],
                              characters_with_blocks: Set[str]):
        render_character_paths(self, char_points, char_bounds, characters, characters_with_blocks)

    def _resolve_event_place(self, event, lane_map):
        """which lane/place an event should be placed in"""
        return self.event_manager.resolve_place(event, lane_map)

    def _assign_parallel_columns(self, lane_events):
        if not lane_events:
            return

        lane_events.sort(key=lambda item: (item['start_offset'], -(item['end_offset'] - item['start_offset'])))
        columns_end: List[int] = []

        for info in lane_events:
            assigned = None
            for index, last_end in enumerate(columns_end):
                if info['start_offset'] > last_end:
                    assigned = index
                    columns_end[index] = info['end_offset']
                    break
            if assigned is None:
                assigned = len(columns_end)
                columns_end.append(info['end_offset'])
            info['column'] = assigned

        column_count = max(1, len(columns_end))
        for info in lane_events:
            info['column_count'] = column_count

    def handle_click(self, payload):
        """Handle graphics click events"""
        return self.click_handler.handle_click(payload)

    def handle_label_menu(self, scene_pos, payload):
        """Handle right-click on labels"""
        return self.click_handler.handle_label_menu(scene_pos, payload)

    def handle_item_menu(self, scene_pos, payload):
        """Handle right-click on items"""
        return self.click_handler.handle_item_menu(scene_pos, payload)

    def show_event(self, event):
        self.info_dialogs.show_event(event)

    def show_char(self, character):
        self.info_dialogs.show_char(character)

    def show_place(self, place):
        self.info_dialogs.show_place(place)

    def _measure_participant_blocks(self, participants, available_width):
        """let layout manager for participant block measurements"""
        return self.layout_manager.measure_blocks(participants, available_width)

    def _place_chars(self, place_id):
        """Get character names in events at this place"""
        if not hasattr(self.project, 'events') or not hasattr(self.project, 'characters'):
            return []
        char_ids = set()
        for event in self.project.events:
            if hasattr(event, 'associated_places') and place_id in getattr(event, 'associated_places', []):
                char_ids.update(getattr(event, 'participants', []))
        id_to_name = {char.id: char.name for char in self.project.characters}
        return [id_to_name.get(cid, cid) for cid in char_ids]

    def _events_overlap(self, event1, event2):
        """Check event overlap via the main controller helper."""
        overlap_checker = getattr(self.main_controller, '_events_overlap', None)
        if callable(overlap_checker):
            return overlap_checker(event1, event2)
        return True

    def _required_event_height(self, participants, available_width):
        base_height = 44.0
        participants = list(participants or [])
        if not participants:
            return base_height + 8.0
        measurements, _, _, _, _, _, block_spacing = self._measure_participant_blocks(participants, available_width)
        blocks_height = sum(height for height, _ in measurements)
        spacing = block_spacing * (len(measurements) - 1) if len(measurements) > 1 else 0.0
        return base_height + blocks_height + spacing + 8.0

    def _get_character_drop_target_event(self, char_rect):
        """Get drop metadata for a dragged character graphic."""
        return self.drag_drop_manager.get_drop_target(char_rect)


    def _move_character_to_top_immediate(self, character, event):
        """Move the character to the top of the event’s participant list and update data"""
        return self.character_manager.move_to_top_now(character, event)


    def _validate_move(self, character, target_event, source_event=None):
        """Validate if character can be moved to target event."""
        return self.validation_manager.validate_move(character, target_event, source_event)
