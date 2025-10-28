class TimelineDataManager:
    """Handles all data"""

    def __init__(self, timeline_controller):
        self.controller = timeline_controller
        self.processor = timeline_controller.data_processor

    def get_events(self, display_mode):
        """Get events for current display mode"""
        return self.processor.get_events(display_mode)
    
    def get_character_names(self, character_ids):
        """Get character names"""
        return self.processor.get_character_names(character_ids)

    def get_event_names(self, event_ids):
        """Get event names"""
        return self.processor.get_event_names(event_ids)

    def get_place_names(self, place_ids):
        """Get place names"""
        return self.processor.get_place_names(place_ids)