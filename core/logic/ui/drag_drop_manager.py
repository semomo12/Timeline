from PySide6.QtCore import Qt

class TimelineDragDropManager:
    """Manages drag & drop"""

    def __init__(self, timeline_controller):
        self.timeline_controller = timeline_controller
        self.scene = timeline_controller.scene
        self.main_controller = getattr(timeline_controller, 'main_controller', None)

    def get_drop_target(self, char_rect):
        """Get drop target info"""
        scene_rect = char_rect.sceneBoundingRect()
        items_in_region = []
        for scene_item in self.scene.items(scene_rect, Qt.IntersectsItemShape):
            items_in_region.append(scene_item)

        best_event = None
        best_overlap = 0.0
        for item in items_in_region:
            if item == char_rect:
                continue
            data = item.data(0)
            if not data:
                continue
            if not isinstance(data, dict):
                continue
            if data.get('kind') != 'event':
                continue
            other_rect = item.sceneBoundingRect()
            overlap = scene_rect.intersected(other_rect)
            if overlap.isValid():
                overlap_area = overlap.width() * overlap.height()
            else:
                overlap_area = 0.0
            if overlap_area > best_overlap:
                best_overlap = overlap_area
                best_event = data.get('event')

        if not best_event:
            return None

        drop_center_y = scene_rect.center().y()
        insert_index = self.calc_insert_indx(best_event, drop_center_y, char_rect)
        return {
            'event': best_event,
            'index': insert_index,
        }

    def calc_insert_indx(self, event, drop_center_y, dragged_item):
        """Estimate insert index based on drop position."""
        participants = getattr(event, 'participants', None)
        if not participants:
            return 0

        candidate_positions = []
        for item in self.scene.items():
            if item is dragged_item:
                continue
            data = item.data(0)
            if not data or not isinstance(data, dict):
                continue
            if data.get('kind') != 'character':
                continue
            if data.get('event') is not event:
                continue
            candidate_positions.append(item.sceneBoundingRect().center().y())

        candidate_positions.sort()
        for index, center_y in enumerate(candidate_positions):
            if drop_center_y < center_y:
                return index
        return len(candidate_positions)
