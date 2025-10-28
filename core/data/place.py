from core.data.base_model import BaseModel

class Place(BaseModel):
    id_count = 1
    
    def __init__(self, name="", description=""):
        super().__init__(name, description)
        self.id = self._make_id()
        self.coordinates = ""
        self.parent = ""
        self.events = []
        self.characters = []
        self.color = ""
        self.associated_events = []
        self.image = ""  

    @classmethod
    def from_dict(cls, data):
        place = cls(data.get('name', ''), data.get('description', ''))
        place.id = data.get('id', place._make_id())
        place.coordinates = data.get('coordinates', '')
        place.parent = data.get('parent', '')
        place.events = data.get('events', [])
        place.characters = data.get('characters', [])
        place.color = data.get('color', '')
        place.associated_events = data.get('associated_events', [])
        place.image = data.get('image', '')
        if place.image and not place.files:
            place.files = [place.image]
        if not place.image and place.files:
            place.image = place.files[0]

        cls._sync_id_counter(place.id)
        return place
     
    @classmethod
    def _sync_id_counter(cls, identifier):
        """Ensure ID counter is always higher than any restored ID"""
        if not identifier or not identifier.startswith("PLA"):
            return
        suffix = identifier[3:]
        if suffix.isdigit():
            number = int(suffix)
            if number >= cls.id_count:
                cls.id_count = number + 1

    def _make_id(self):
        pid = f"PLA{Place.id_count:03d}"
        Place.id_count += 1
        return pid

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'coordinates': self.coordinates,
            'parent': self.parent,
            'events': self.events,
            'characters': self.characters,
            'color': self.color,
            'associated_events': self.associated_events,
            'image': self.image or (self.files[0] if self.files else ''),
        })
        return data

    def __str__(self):
        """place text info """
        if self.parent:
            return f"Place: {self.name} ({self.parent})"
        else:
            return f"Place: {self.name}"
