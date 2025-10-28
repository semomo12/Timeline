from PySide6.QtWidgets import QMessageBox

class TimelineValidationManager:
    """validation for timeline operations."""

    def __init__(self, timeline_controller):
        self.timeline_controller = timeline_controller

    def validate_char_events(self, selected_event_ids):
        """Validate that selected events don't overlap in time."""
        if not selected_event_ids or len(selected_event_ids) < 2:
            return True
        events_by_id = {}
        for event in self.timeline_controller.project.events:
            events_by_id[event.id] = event

        selected_events = []
        for event_id in selected_event_ids:
            if event_id in events_by_id:
                selected_events.append(events_by_id[event_id])

        event_count = len(selected_events)
        for index in range(event_count):
            first = selected_events[index]
            for other_index in range(index + 1, event_count):
                second = selected_events[other_index]
                if self.timeline_controller._events_overlap(first, second):
                    QMessageBox.warning(
                        None,
                        'Event Overlap',
                        f'"{first.name}" and "{second.name}" overlap in time. Please pick events that do not occur simultaneously.'
                    )
                    return False
        return True

    def validate_events(self, selected_event_ids):
        return self.validate_char_events(selected_event_ids)

    def check_char_overlap(self, character, event):
        """Check if character has overlapping events with the given event."""
        if not hasattr(character, 'associated_events'):
            return False
        character_events = getattr(character, 'associated_events', [])
        for event_id in character_events:
            existing_event = None
            for candidate in self.timeline_controller.project.events:
                if candidate.id == event_id:
                    existing_event = candidate
                    break
            if existing_event and existing_event.id != event.id:
                if self.timeline_controller._events_overlap(existing_event, event):
                    return True
        return False

    def validate_event_chars(
        self,
        event_name,
        start_date,
        end_date,
        timeline_mode,
        day_index,
        day_index_end,
        character_ids,
        event_id=None,
    ):
        """Validate that selected characters don't participate in overlapping events."""
        if not character_ids:
            return True

        temp_event = type('TempEvent', (), {})()
        temp_event.name = event_name
        temp_event.start_date = start_date
        temp_event.end_date = end_date
        temp_event.timeline_mode = timeline_mode
        temp_event.day_index = day_index
        temp_event.day_index_end = day_index_end
        temp_event.id = event_id

        for char_id in character_ids:
            character = None
            for candidate in self.timeline_controller.project.characters:
                if candidate.id == char_id:
                    character = candidate
                    break
            if not character or not hasattr(character, 'associated_events'):
                continue

            for existing_event_id in character.associated_events:
                if event_id and existing_event_id == event_id:
                    continue
                existing_event = None
                for event in self.timeline_controller.project.events:
                    if event.id == existing_event_id:
                        existing_event = event
                        break
                if existing_event and self.timeline_controller._events_overlap(temp_event, existing_event):
                    QMessageBox.warning(
                        None,
                        'Character Conflict',
                        f'Character "{character.name}" is already participating in event "{existing_event.name}" '
                        f'which overlaps with "{event_name}".\n\n'
                        f'Characters cannot participate in events that occur simultaneously.'
                    )
                    return False
        return True

    def validate_move(self, character, target_event, source_event=None):
        """Validate if a character move to target event."""
        try:
            if hasattr(target_event, 'participants') and character.id in target_event.participants:
                print(f"Character {character.name} already exists in event {target_event.name}")
                return False
            if hasattr(target_event, 'characters') and character in target_event.characters:
                print(f"Character {character.name} already exists in event {target_event.name}")
                return False
            if hasattr(character, 'associated_events'):
                character_event_ids = list(character.associated_events)

                if target_event.id in character_event_ids:
                    character_event_ids.remove(target_event.id)

                if source_event and source_event.id in character_event_ids:
                    character_event_ids.remove(source_event.id)

                events_by_id = {}
                for event in self.timeline_controller.project.events:
                    events_by_id[event.id] = event

                remaining_events = []
                for event_id in character_event_ids:
                    if event_id in events_by_id:
                        remaining_events.append(events_by_id[event_id])

                for existing_event in remaining_events:
                    if self.timeline_controller._events_overlap(target_event, existing_event):
                        QMessageBox.warning(
                            None,
                            'Event Overlap',
                            f'Cannot move character "{character.name}" to "{target_event.name}".\n\n'
                            f'"{target_event.name}" and "{existing_event.name}" overlap. '
                            f'Characters cannot participate in events that occur simultaneously.'
                        )
                        return False
            return True
        except Exception as error:
            print(f"Error validating character move: {error}")
            return False
