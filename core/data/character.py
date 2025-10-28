import random
from core.data.base_model import BaseModel

class Character(BaseModel):
    """Character model"""

    COLORS = [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
        "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9"
    ]
    used_colors = set()
    id_counter = 1

    def __init__(self, name="", description=""):
        super().__init__(name, description)

        self.id = str(Character.id_counter)
        Character.id_counter += 1
        self.age = None
        self.aliases = []
        self.color = self.get_unique_color()
        self.events = []
        self.places = []
        self.associated_places = []

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'age': self.age,
            'aliases': self.aliases,
            'color': self.color,
            'events': self.events,
            'places': self.places,
            'associated_places': self.associated_places
        })
        return data
    @classmethod
    def from_dict(cls, data):
        """Create character"""
        character = super().from_dict(data)
        if not isinstance(character, cls):
            character = cls()
        character.age = data.get('age')
        character.aliases = data.get('aliases', [])

        character.color = data.get('color', cls().get_unique_color())
        character.events = data.get('events', [])
        character.places = data.get('places', [])
        character.associated_places = data.get('associated_places', [])
        return character

    def get_unique_color(self):
        """Get unique color"""
        for color in self.COLORS:
            if color not in self.used_colors:
                self.used_colors.add(color)
                return color

        # generate a random color if all colors are used
        return f"#{random.randint(0, 0xFFFFFF):06X}"

    def __str__(self):
        """Return the object info as a readable string"""
        age_info = f", age: {self.age}" if self.age else ""
        return f"Character: {self.name}{age_info}"
