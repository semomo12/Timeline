from PySide6.QtGui import QFont, QFontMetrics

class TimelineLayoutManager:
    """Manages layout for timeline objects"""

    def __init__(self, timeline_controller):
        self.timeline_controller = timeline_controller
        self.main_controller = timeline_controller.main_controller
        self.DAY_WIDTH = timeline_controller.DAY_WIDTH
        self.LANE_HEIGHT = timeline_controller.LANE_HEIGHT
        self.LEFT_MARGIN = timeline_controller.LEFT_MARGIN
        self.TOP_MARGIN = timeline_controller.TOP_MARGIN
        self.LANE_PADDING = timeline_controller.LANE_PADDING

    def build_lane_order(self, events, places):
        lanes = []
        places_list = list(places.values())
        places_list.reverse()
        for place in places_list:
            lanes.append((place.id, place.name))
        lane_labels = {}
        for lane in lanes:
            lane_id = lane[0]
            label = lane[1]
            lane_labels[lane_id] = label

        has_no_place = False
        for item in events:
            event_obj = item['event']
            assoc = getattr(event_obj, 'associated_places', None)
            if not assoc:
                has_no_place = True
                continue
            for place_id in assoc:
                if place_id not in lane_labels:
                    lane_labels[place_id] = "Place " + str(place_id)
                    lanes.append((place_id, lane_labels[place_id]))

        if not lanes or has_no_place:
            new_lanes = []
            new_lanes.append(("__NO_PLACE__", "No Place"))
            for lane in lanes:
                if lane[0] != "__NO_PLACE__":
                    new_lanes.append(lane)
            lanes = new_lanes
        return lanes

    def measure_blocks(self, participants, available_width):
        """Calculate how much space is needed to show all participants."""
        font = QFont("Arial", 8)
        metrics = QFontMetrics(font)
        measurements = []
        padding_x = 8.0
        padding_y = 6.0
        block_spacing = 2.0
        min_block_width = 72.0
        text_width = available_width - 2 * padding_x
        for character in participants:
            text_rect = metrics.boundingRect(character.name)
            block_height = max(20.0, text_rect.height() + 2 * padding_y)
            block_width = max(min_block_width, min(text_rect.width() + 2 * padding_x, available_width))
            measurements.append((block_height, block_width))
        return measurements, font, metrics, text_width, padding_x, padding_y, block_spacing

    def lane_layout(self, lane_items, events):
        lane_event_map = {}
        for lane in lane_items:
            lane_id = lane[0]
            lane_event_map[lane_id] = []
            for event in events:
                event_obj = event.event if hasattr(event, 'event') else event['event'] if isinstance(event, dict) and 'event' in event else None
                if event_obj and lane_id in getattr(event_obj, 'associated_places', []):
                    lane_event_map[lane_id].append(event)
        return self.calc_lane_layout(lane_items, lane_event_map, self.LANE_HEIGHT, self.TOP_MARGIN)

    def assign_columns(self, lane_events):
        if not lane_events:
            return
        def sort_key(item):
            return (item['start_offset'], -(item['end_offset'] - item['start_offset']))
        lane_events.sort(key=sort_key)
        columns_end = []
        for info in lane_events:
            assigned = None
            for index in range(len(columns_end)):
                last_end = columns_end[index]
                if info['start_offset'] > last_end:
                    assigned = index
                    columns_end[index] = info['end_offset']
                    break
            if assigned is None:
                assigned = len(columns_end)
                columns_end.append(info['end_offset'])
            info['column'] = assigned
        column_count = 1
        if len(columns_end) > 1:
            column_count = len(columns_end)
        for info in lane_events:
            info['column_count'] = column_count

    def event_height(self, participants, available_width):
        base_height = 44.0
        if not participants:
            return base_height + 8.0
        blocks_height = 28.0 * len(participants)
        if len(participants) > 1:
            spacing = 6.0 * (len(participants) - 1)
        else:
            spacing = 0.0
        return base_height + blocks_height + spacing + 8.0

    def lane_layout(self, lane_items, lane_event_map, lane_height=160.0, top_margin=80.0):
        lane_heights = []
        for lane_id, _ in lane_items:
            events = lane_event_map.get(lane_id, [])
            required_height = lane_height
            for info in events:
                column_count = max(1, info.get('column_count', 1))
                approx_width = info.get('approx_width', 80.0)
                event_slot_height = self.event_height(info.get('participants', []), approx_width)
                lane_needed = 32.0 + event_slot_height * column_count + 56.0
                if lane_needed > required_height:
                    required_height = lane_needed
            lane_heights.append(required_height)
        lane_tops = {}
        current_top = top_margin
        for (lane_id, _), lane_height in zip(lane_items, lane_heights):
            lane_tops[lane_id] = current_top
            current_top += lane_height
        total_height = current_top + 120.0
        return lane_heights, lane_tops, total_height

