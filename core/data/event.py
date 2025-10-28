from core.data.base_model import BaseModel

class Event(BaseModel):
    """Event model"""

    id_count = 1

    def __init__(self, name="", description=""):
        super().__init__(name, description)
        self.id = self._make_id()
        self.start_date = ""
        self.end_date = ""
        self.location = ""
        self.participants = []
        self.related_events = []
        self.places = []
        self.timeline_mode = "calendar"
        self.display_mode = "span"
        self.day_number = None
        self.day_number_end = None
        self.day_index = None
        self.day_index_end = None
        self.associated_places = []

    def _make_id(self):
        eid = f"EVE{Event.id_count:03d}"
        Event.id_count += 1
        return eid

    def to_dict(self):
        """make dictionary"""
        data = super().to_dict()
        day_index = getattr(self, 'day_index', None)
        day_index_end = getattr(self, 'day_index_end', None)
        day_number = getattr(self, 'day_number', None)
        if day_number is None:
            day_number = day_index
        day_number_end = getattr(self, 'day_number_end', None)
        if day_number_end is None:
            day_number_end = day_index_end
        data.update({
            'start_date': getattr(self, 'start_date', ''),
            'end_date': getattr(self, 'end_date', ''),
            'location': getattr(self, 'location', ''),
            'participants': getattr(self, 'participants', []),
            'related_events': getattr(self, 'related_events', []),
            'places': getattr(self, 'places', []),
            'timeline_mode': getattr(self, 'timeline_mode', 'calendar'),
            'day_number': day_number,
            'day_number_end': day_number_end,
            'day_index': day_index,
            'day_index_end': day_index_end,
            'display_mode': getattr(self, 'display_mode', 'span'),
            'associated_places': getattr(self, 'associated_places', [])
        })
        return data

    @classmethod
    def from_dict(cls, data):
        """Create event"""
        event = super().from_dict(data)
        event.start_date = data.get('start_date', '')
        event.end_date = data.get('end_date', '')
        event.location = data.get('location', '')
        event.participants = cls._clean_list(data.get('participants', []))
        event.related_events = cls._clean_list(data.get('related_events', []))
        event.places = cls._clean_list(data.get('places', []))
        event.timeline_mode = data.get('timeline_mode', 'calendar')
        event.day_number = data.get('day_number', data.get('day_index'))
        event.day_number_end = data.get('day_number_end', data.get('day_index_end'))
        event.display_mode = data.get('display_mode', 'span')
        event.day_index = data.get('day_index', data.get('day_number'))
        event.day_index_end = data.get('day_index_end', data.get('day_number_end'))
        event.associated_places = data.get('associated_places', data.get('places', []))
        if event.timeline_mode == 'day_sequence':
            if event.day_index is None:
                event.day_index = cls._parse_day_value(event.start_date)
            if event.day_index_end is None:
                event.day_index_end = cls._parse_day_value(event.end_date)
        if event.day_number is None:
            event.day_number = event.day_index
        if event.day_number_end is None:
            event.day_number_end = event.day_index_end
        return event

    @staticmethod
    def _parse_day_value(value):
        """Extract numeric day value from a string like 'Day 1'."""
        if not isinstance(value, str):
            return None
        digits = ''.join(ch for ch in value if ch.isdigit())
        if not digits:
            return None
        try:
            number = int(digits)
        except ValueError:
            return None
        return number if number > 0 else None

    @staticmethod
    def _clean_list(items):
        """Clean list"""
        if not isinstance(items, list):
            return []

        clean_items = []
        seen = set()
        for item in items:
            if item and item not in seen:  # Remove duplicates and empty items
                clean_items.append(str(item))
                seen.add(item)
        return clean_items

    def __str__(self):
        """Returns a text representation of the event"""
        date_info = f" ({self.start_date}"
        if self.end_date:
            date_info += f" to {self.end_date}"
        date_info += ")"
        return f"Event: {self.name}{date_info}"
