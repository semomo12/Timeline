from datetime import datetime
from PySide6.QtWidgets import QMessageBox

class HelperController:
    """helper for controllers."""

    def __init__(self, main_controller):
        self.main_controller = main_controller

    @property
    def project(self):
        return getattr(self.main_controller, "project", None)

    def show_info_message(self, title, message):
        print(f"{title}: {message}")

    def maybe_save_before_action(self, action_description="performing this action"):
        has_dirty_flag = getattr(self.main_controller, "project_dirty", False)
        if not has_dirty_flag:
            return True

        reply = QMessageBox.question(
            self.main_controller,
            "Unsaved Changes",
            f"You have unsaved changes. Do you want to save before {action_description}?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
        )
        if reply == QMessageBox.Yes:
            project_controller = getattr(self.main_controller, "project_controller", None)
            if project_controller and hasattr(project_controller, "save"):
                return project_controller.save()
            return False
        if reply == QMessageBox.No:
            return True
        return False

    @staticmethod
    def normalize_name(name):
        return name.strip().lower()

    def is_name_taken(self, entity_type, name, exclude_id=None):
        project = self.project
        if not project:
            return False
        if entity_type == "character":
            entities = project.characters
        elif entity_type == "event":
            entities = project.events
        elif entity_type == "place":
            entities = project.places
        else:
            return False
        check_name = self.normalize_name(name)

        for entity in entities:
            entity_id = getattr(entity, "id", None)
            if exclude_id and entity_id == exclude_id:
                continue
            entity_name = getattr(entity, "name", "")
            if self.normalize_name(entity_name) == check_name:
                return True
        return False

    def update_char_places(self, character):
        project = self.project
        if not project:
            character.associated_places = []
            return
        associated_events = getattr(character, "associated_events", [])
        place_ids = set()
        for event_id in associated_events:
            event = self._find_event_by_id(event_id)
            if not event:
                continue
            event_places = getattr(event, "associated_places", [])
            for place_id in event_places:
                place_ids.add(place_id)

        character.associated_places = list(place_ids)

    def check_char_overlap(self, character, new_event):
        if not character or not new_event:
            return False
        project = self.project
        if not project:
            return False
        associated_events = getattr(character, "associated_events", [])

        for event_id in associated_events:
            existing_event = self._find_event_by_id(event_id)
            if existing_event and self._events_overlap(existing_event, new_event):
                return True
        return False

    def get_place_chars(self, place_id):
        project = self.project
        if not project:
            return []
        character_ids = set()
        for event in project.events:
            places = getattr(event, "associated_places", [])
            if place_id in places:
                participants = getattr(event, "participants", [])
                for participant_id in participants:
                    character_ids.add(participant_id)
        return list(character_ids)

    def get_char_places(self, character):
        project = self.project
        if not project:
            return "—"
        associated_events = getattr(character, "associated_events", [])
        place_ids = set()

        for event_id in associated_events:
            event = self._find_event_by_id(event_id)
            if not event:
                continue
            event_places = getattr(event, "associated_places", [])
            for place_id in event_places:
                place_ids.add(place_id)

        if not place_ids:
            return "—"
        place_names = []
        for place in project.places:
            if place.id in place_ids:
                place_names.append(place.name)
        if not place_names:
            return "—"

        return ", ".join(place_names)

    def next_day_index(self):
        project = self.project
        if not project or not hasattr(project, "events"):
            return 1
        highest_index = 0
        for event in project.events:
            for attribute in ("day_index", "day_index_end"):
                value = getattr(event, attribute, None)
                number = self._parse_day_index(value)
                if number is not None and number > highest_index:
                    highest_index = number
        if highest_index >= 1:
            return highest_index + 1
        else:
            return 1

    def _parse_day_index(self, value):
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            return None
        lowered = text.lower()
        if lowered.startswith("day"):
            digits = "".join(character for character in text if character.isdigit())
            if digits:
                try:
                    return max(1, int(digits))
                except ValueError:
                    return None
        if text.isdigit():
            try:
                return max(1, int(text))
            except ValueError:
                return None
        return None

    @staticmethod
    def deduplicate_ids(id_list):
        seen = set()
        result = []
        for item in id_list or []:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result

    @staticmethod
    def append_unique(container, value):
        if value and value not in container:
            container.insert(0, value)

    @staticmethod
    def parse_date(value):
        if value is None:
            return None
        text = value.strip()
        if not text:
            return None

        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(text).date()
        except ValueError:
            return None

    def _events_overlap(self, first_event, second_event):
        mode_a, start_a, end_a = self._event_time_range(first_event)
        mode_b, start_b, end_b = self._event_time_range(second_event)

        if start_a is None or start_b is None:
            return False
        if mode_a == "day_sequence" and mode_b == "day_sequence":
            return start_a <= end_b and start_b <= end_a
        if mode_a == "calendar" and mode_b == "calendar":
            return start_a <= end_b and start_b <= end_a
        return False

    def _event_time_range(self, event):
        mode = getattr(event, "timeline_mode", "calendar") or "calendar"

        if mode == "day_sequence":
            start = getattr(event, "day_index", None)
            end = getattr(event, "day_index_end", None)
            if start is None:
                start_str = getattr(event, "start_date", "")
                start = self._parse_day_index(start_str) if start_str else None
            
            if end is None:
                end_str = getattr(event, "end_date", "")
                end = self._parse_day_index(end_str) if end_str else None
            if start is None:
                return mode, None, None
            try:
                start = int(start)
                if end is not None:
                    end = int(end)
            except (ValueError, TypeError):
                return mode, None, None
            
            if end is None or end < start:
                end = start
            return mode, start, end

        start_date = self.parse_date(getattr(event, "start_date", ""))
        end_date = self.parse_date(getattr(event, "end_date", ""))
        if start_date is None:
            return mode, None, None
        if end_date is None or end_date < start_date:
            end_date = start_date
        return mode, start_date, end_date

    def _find_event_by_id(self, event_id):
        project = self.project
        if not project:
            return None
        for event in project.events:
            if getattr(event, "id", None) == event_id:
                return event
        return None

def resolve_event_names(data_manager, identifiers):
    return data_manager.event_names(identifiers)

def resolve_place_names(data_manager, identifiers):
    return data_manager.place_names(identifiers)

def collect_image_paths(files):
    paths = []
    for item in files:
        if hasattr(item, "path"):
            paths.append(getattr(item, "path"))
        elif isinstance(item, str):
            paths.append(item)
    return paths
