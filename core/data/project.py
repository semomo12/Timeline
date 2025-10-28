import json
from core.data.character import Character
from core.data.event import Event
from core.data.place import Place

class Project:
    """Main project"""

    def __init__(self):
        self.name = "My Project"
        self.characters = []
        self.events = []
        self.places = []
        self.metadata = {}

    @classmethod
    def from_json(cls, data):
        """Create Project from JSON dict"""
        proj = cls()
        proj.name = data.get('name', 'My Project')
        proj.characters = [Character.from_dict(c) for c in data.get('characters', [])]
        proj.events = [Event.from_dict(e) for e in data.get('events', [])]
        proj.places = [Place.from_dict(p) for p in data.get('places', [])]
        proj.metadata = data.get('metadata', {})
        return proj

    def to_dict(self):
        """dictionary"""
        return {
            'name': self.name,
            'characters': [char.to_dict() for char in self.characters],
            'events': [event.to_dict() for event in self.events],
            'places': [place.to_dict() for place in self.places],
            'metadata': self.metadata
        }

    def to_json(self, *, indent=2):
        """Serialize project to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def get_character(self, character_id):
        """Get character by ID"""
        for char in self.characters:
            if char.id == character_id:
                return char
        return None

    def __str__(self):
        """Show project """
        chars = len(self.characters)
        events = len(self.events)
        places = len(self.places)
        return f"{self.name}: {chars} chars, {events} events, {places} places"
