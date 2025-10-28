
""" Unit tests for creating and editing Character, Event and Place"""

import pytest
from core.data.character import Character
from core.data.event import Event
from core.data.place import Place
from core.data.project import Project

class TestCharacterOperations:
    """Tests Character-operations"""

    def test_create_characters(self):
        char = Character("Jane", "A character")
        char.age = 25
        assert char.age == 25
        assert char.name == "Jane"

    def test_character_from_dict(self):
        data = {
            "id": "CHAR001",
            "name": "Anna",
            "description": "Test character",
            "age": 18,
            "color": "#FF6B6B",
            "notes": "Test notes",
            "associated_places": ["PLA001", "PLA002"]
        }
        
        char = Character.from_dict(data)
        assert char.name == "Anna"
        assert char.age == 18
        assert char.color == "#FF6B6B"
        assert len(char.associated_places) == 2

    def test_edit_character(self):
        char = Character("Original Name", "Original description")
        original_id = char.id
        char.name = "Updated Name"
        char.description = "Updated description"
        char.age = 42
        char.notes = "New notes"
        
        assert char.name == "Updated Name"
        assert char.description == "Updated description"
        assert char.age == 42
        assert char.notes == "New notes"
        assert char.id == original_id  

    def test_character_images(self):
        char = Character("FileTest")
        char.files = ["/path/to/image1.jpg", "/path/to/image2.png"]
        
        assert len(char.files) == 2
        assert char.files[0] == "/path/to/image1.jpg"


class TestEventOperations:
    """Tests Event-operations"""

    def test_create_event(self):
        event = Event("Meeting", "mentor meeting")
        assert event.name == "Meeting"
        assert event.description == "mentor meeting"
        assert event.id is not None
        assert event.id.startswith("EVE")
        assert event.timeline_mode == "calendar"

    def test_event_by_day_sequence(self):
        event = Event("war", "Epic battle")
        event.timeline_mode = "day_sequence"
        event.day_index = 6
        event.day_index_end = 7000
        
        assert event.timeline_mode == "day_sequence"
        assert event.day_index == 6
        assert event.day_index_end == 7000

    def test_event_add_participants(self):
        event = Event("Workshop")
        event.participants = []
        event.participants.append("CHAR001")
        event.participants.append("CHAR002")
    
        assert len(event.participants) == 2
        assert "CHAR001" in event.participants


class TestPlaceOperations:
    """Tests for Place operations"""

    def test_place_from_dict(self):
        data = {
            "id": "PLA456",
            "name": "skolan",
            "description": "demo3",
            "coordinates": "55.6761,12.5683",
            "parent": "Classroom A",
            "associated_events": ["EVE003"]
        }
        
        place = Place.from_dict(data)
        assert place.name == "skolan"
        assert place.coordinates == "55.6761,12.5683"
        assert place.parent == "Classroom A"
        assert len(place.associated_events) == 1

    def test_place_add_events(self):
        place = Place("skogen")
        place.associated_events = []
        place.associated_events.append("EVE001")
        place.associated_events.append("EVE002")
        
        assert len(place.associated_events) == 2
        assert "EVE001" in place.associated_events

class TestProjectIntegration:
    """Integrationstests for entitets"""

    def test_create_project_with_entities(self):
        project = Project()
        project.name = "Test Timeline"
        
        char = Character("katniss", "Main character")
        project.characters.append(char)
        
        place = Place("District12", "kapital i hungerspelen")
        project.places.append(place)
        
        event = Event("spel", "spel i hungerspelen")
        event.start_date = "2025-10-01"
        event.participants = [char.id]
        event.associated_places = [place.id]
        project.events.append(event)
        
        assert len(project.characters) == 1
        assert len(project.places) == 1
        assert len(project.events) == 1
        assert project.events[0].participants[0] == char.id

    def test_entity_relationships(self):
        project = Project()
        
        char1 = Character("Prim", "Character 1")
        char2 = Character("Gale", "Character 2")
        place = Place("District12", "home")
        event = Event("Intervju", "Interview event")
        
        event.participants = [char1.id, char2.id]
        event.associated_places = [place.id]
        char1.associated_events = [event.id]
        char2.associated_events = [event.id]
        place.associated_events = [event.id]
  
        project.characters.extend([char1, char2])
        project.places.append(place)
        project.events.append(event)

        assert len(event.participants) == 2
        assert char1.id in event.participants
        assert char2.id in event.participants
        assert place.id in event.associated_places
        assert event.id in char1.associated_events
        assert event.id in place.associated_events

    def test_get_character_by_id(self):
        project = Project()
        char = Character("FindCharacter", "Test character")
        project.characters.append(char)
        found = project.get_character(char.id)
        
        assert found is not None
        assert found.name == "FindCharacter"
        assert found.id == char.id
        not_found = project.get_character("NONEXISTENT")
        assert not_found is None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
