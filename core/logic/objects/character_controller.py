from PySide6.QtGui import QTextOption
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox,QInputDialog,QDialog,QFormLayout,QLineEdit,QTextEdit,QSpinBox,QDialogButtonBox
from core.data.character import Character
from core.utils.timeline_helpers import HelperController
from core.logic.objects.base_controller import BaseEntityController
from typing import Any, Dict, List

class CharacterController(BaseEntityController):
    """Manages character operations"""
    
    def __init__(self, main_controller):
        self.main_controller = main_controller

    def move_to_event_now(self, character, source_event, target_event, insert_index=None):
        """Move to event"""
        if not (character and source_event and target_event):
            return False

        if hasattr(source_event, "participants") and character.id in source_event.participants:
            remaining = []
            for cid in source_event.participants:
                if cid != character.id:
                    remaining.append(cid)
            source_event.participants = remaining

        if hasattr(target_event, "participants"):
            target_participants = [cid for cid in target_event.participants if cid != character.id]
            if insert_index is None:
                insert_index = len(target_participants)
            insert_index = max(0, min(insert_index, len(target_participants)))
            target_participants.insert(insert_index, character.id)
            target_event.participants = target_participants

        if hasattr(character, "associated_events"):
            if target_event.id not in character.associated_events:
                character.associated_events.insert(0, target_event.id)
            if source_event.id in character.associated_events:
                character.associated_events = [eid for eid in character.associated_events if eid != source_event.id]

        self.main_controller._update_character_places_from_events(character)
        self.main_controller.mark_project_dirty()
        self.main_controller._update_ui()
        return True

    def move_to_top_now(self, character, event):
        """Move characters to top of list in event"""
        return self.reposition_within_event_now(character, event, 0)

    def reposition_within_event_now(self, character, event, insert_index=None):
        """Moves a character within an event to a new position."""
        if character is None or event is None:
            return False

        if not hasattr(event, "participants"):
            return False

        if not isinstance(event.participants, list):
            return False

        new_list = []
        for cid in event.participants:
            if cid != character.id:
                new_list.append(cid)

        if insert_index is None:
            insert_index = 0

        if insert_index < 0:
            insert_index = 0
        if insert_index > len(new_list):
            insert_index = len(new_list)

        new_list.insert(insert_index, character.id)
        event.participants = new_list

        self.main_controller.mark_project_dirty()
        self.main_controller._update_ui()
        return True
        
    def sync_character_events(self, character, previous_events=None):
        """helper to sync character's events"""
        if previous_events is None:
            previous_events = set()
        current_events = set(character.associated_events or [])

        for event in getattr(self.main_controller.project, "events", []):
            participants = getattr(event, "participants", None)
            if not isinstance(participants, list):
                event.participants = []
                participants = event.participants

            if event.id in current_events:
                self.main_controller.helper_controller.append_unique(event.participants, character.id)
            elif event.id in previous_events and character.id in participants:
                filtered = []
                for cid in participants:
                    if cid != character.id:
                        filtered.append(cid)
                event.participants = filtered
    def apply_form_to_character(self, character, form_data, *, fallback_name=None):
        """helper to apply form data to character"""
        if fallback_name is None:
            fallback_name = character.name
        name_value = form_data.get("name", fallback_name)
        if name_value is not None:
            character.name = name_value

        character.description = form_data.get("description", "") or ""

        files_value = form_data.get("files", [])
        if isinstance(files_value, list):
            character.files = list(files_value)
        else:
            character.files = []

        character.age = form_data.get("age")
        character.notes = form_data.get("notes", "") or ""

        event_ids = form_data.get("events", [])
        if event_ids is None:
            event_ids = []
        character.associated_events = HelperController.deduplicate_ids(event_ids)
        
        
    def add(self):
        """Add a new character"""
        form_data = self._dialog()
        if not form_data:
            return

        character_name = form_data.get("name", "")
        if self.main_controller.is_name_taken("character", character_name):
            QMessageBox.warning(
                self.main_controller,
                "Duplicate Name",
                "A character with this name already exists. Please choose another name.",
            )
            return

        new_character = Character(character_name)
        self.apply_form_to_character(new_character, form_data, fallback_name=character_name)

        self.main_controller._update_character_places_from_events(new_character)
        self.main_controller.project.characters.append(new_character)

        self.sync_character_events(new_character)

        self.main_controller.mark_project_dirty()
        self.main_controller._update_ui()
        QMessageBox.information(
            self.main_controller,
            "Character Added",
            f'Character "{new_character.name}" added!\n ID: {new_character.id}',
        )

    def add_to_event(self, event_id):
        """Add a new character and  associate with event"""
        if not event_id:
            return
        
        target_event = None
        for evt in self.main_controller.project.events:
            if getattr(evt, "id", None) == event_id:
                target_event = evt
                break
        if target_event is None:
            QMessageBox.warning(self.main_controller, 'Event Not Found', 'Could not locate the selected event.')
            return

        data = self._dialog(force_event_id=event_id)
        if not data:
            return
        if self.main_controller.is_name_taken('character', data['name']):
            QMessageBox.warning(self.main_controller, 'Duplicate Name', 'A character with this name already exists. Please choose another name.')
            return
        new_name = data.get('name', '')

        character = Character(new_name)
        self.apply_form_to_character(character, data, fallback_name=new_name)

        if target_event.id not in character.associated_events:
            check_list = list(character.associated_events)
            check_list.append(target_event.id)
            if not self.main_controller.validation_manager.validate_char_events(check_list):
                return
            character.associated_events.insert(0, target_event.id)

        self.main_controller._update_character_places_from_events(character)
        self.main_controller.project.characters.append(character)

        self.sync_character_events(character)

        self.main_controller.mark_dirty()
        self.main_controller._update_ui()
        QMessageBox.information(self.main_controller, 'Character Added to Event',
                                f'Character "{character.name}" created and added to event "{target_event.name}"!\n ID: {character.id}')

    def edit(self):
        """Edit an existing character"""
        characters = self.main_controller.project.characters
        if not characters:
            QMessageBox.information(self.main_controller, "No Characters", "No characters available to edit!")
            return

        options = []
        for char in characters:
            options.append(f"{char.name} ({char.id})")

        selected_item, ok = QInputDialog.getItem(
            self.main_controller,
            "Edit Character",
            "Select character to edit:",
            options,
            0,
            False,
        )
        if not ok or not selected_item:
            return

        chosen_character = None
        if "(" in selected_item and selected_item.endswith(")"):
            start = selected_item.rfind("(") + 1
            char_id = selected_item[start:-1]
            for char in characters:
                if char.id == char_id:
                    chosen_character = char
                    break

        if chosen_character is None:
            selected_name = selected_item.split(" (")[0]
            for char in characters:
                if char.name == selected_name:
                    chosen_character = char
                    break

        if chosen_character is None:
            QMessageBox.warning(self.main_controller, "Character Not Found", "Could not locate the selected character.")
            return

        form_data = self._dialog(chosen_character)
        if not form_data:
            return

        previous_events = set(chosen_character.associated_events)

        self.apply_form_to_character(chosen_character, form_data)

        self.main_controller._update_character_places_from_events(chosen_character)

        self.sync_character_events(chosen_character, previous_events)

        self.main_controller.mark_project_dirty()
        self.main_controller._update_ui()
        QMessageBox.information(
            self.main_controller,
            "Character Updated",
            f'Character "{chosen_character.name}" updated successfully!',
        )

    def edit_by_id(self, character_id):
        """Edit character by id"""
        if not character_id:
            return

        character = None
        for ch in self.main_controller.project.characters:
            if getattr(ch, "id", None) == character_id:
                character = ch
                break

        if character is None:
            QMessageBox.warning(self.main_controller, "Character Not Found", "Could not locate the selected character.")
            return

        form_data = self._dialog(character)
        if not form_data:
            return

        previous_events = set(character.associated_events)

        self.apply_form_to_character(character, form_data)

        self.main_controller._update_character_places_from_events(character)

        self.sync_character_events(character, previous_events)

        self.main_controller.mark_project_dirty()
        self.main_controller._update_ui()
        QMessageBox.information(
            self.main_controller,
            "Character Updated",
            f'Character "{character.name}" updated successfully!',
        )


    def remove(self):
        """Remove a character with selection dialog"""
        characters = self.main_controller.project.characters
        if not characters:
            QMessageBox.information(self.main_controller, 'No Characters', 'No characters to remove!')
            return

        character_items = [f"{char.name} ({char.id})" for char in characters]
        selected_item, ok = QInputDialog.getItem(self.main_controller, 'Remove Character', 'Select character to remove:', character_items, 0, False)
        if not ok or not selected_item:
            return

        character_name = selected_item.split(' (')[0]
        character_to_remove = None
        for char in characters:
            if char.name == character_name:
                character_to_remove = char
                break
        if character_to_remove is None:
            return

        reply = QMessageBox.question(
            self.main_controller, 'Confirm Removal',
            f'Are you sure you want to remove character "{character_name}"?',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.main_controller.project.characters.remove(character_to_remove)
            self.main_controller.mark_project_dirty()
            self.main_controller._update_ui()
            QMessageBox.information(self.main_controller, 'Character Removed', f'Character "{character_name}" removed!')

    
    def _dialog(self, character=None, force_event_id=None):
        """Show character add/edit dialog"""
        dialog = QDialog(self.main_controller)
        if character is None:
            dialog.setWindowTitle("Add Character")
        else:
            dialog.setWindowTitle("Edit Character")
        dialog.setMinimumWidth(500)

        layout = QFormLayout(dialog)
        
        existing_name = ""
        if character is not None and getattr(character, "name", None):
            existing_name = character.name
        name_edit = QLineEdit(existing_name)
        layout.addRow("Name*:", name_edit)
        
        description_edit = QTextEdit()
        description_edit.setMaximumHeight(80)
        description_edit.setMinimumHeight(60)
        description_edit.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)

        description_text = ""
        if character is not None:
            description_text = getattr(character, "description", "") or ""
        if len(description_text) > 200:
            description_text = description_text[:200]
        description_edit.setPlainText(description_text)
        layout.addRow("Description:", description_edit)

        # for view of images
        existing_files = []
        if character is not None:
            stored_files = getattr(character, "files", [])
            if isinstance(stored_files, list):
                for path in stored_files:
                    existing_files.append(path)
        files_widget = self.main_controller.ui_controller.create_image_upload_section(layout, existing_files)

        #Age
        age_spin = QSpinBox()
        age_spin.setRange(0, 1_000_000) #maybe for fictional characters
        age_spin.setSpecialValueText(" ")
        if character is not None and isinstance(getattr(character, "age", None), int):
            age_value = character.age
            if 1 <= age_value <= 1_000_000:
                age_spin.setValue(age_value)
            else:
                age_spin.setValue(0)
        else:
            age_spin.setValue(0)
        layout.addRow("Age:", age_spin)

        notes_edit = QTextEdit()
        notes_edit.setMaximumHeight(60)
        notes_edit.setMinimumHeight(40)
        notes_edit.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        notes_text = ""
        if character is not None:
            notes_text = getattr(character, "notes", "") or ""
        if len(notes_text) > 200:
            notes_text = notes_text[:200]
        notes_edit.setPlainText(notes_text)
        layout.addRow("Notes:", notes_edit)

        places_display = None
        if force_event_id is None:
            places_info = ""
            if character is not None:
                places_info = self.main_controller.helper_controller.get_char_places(character)
            places_display = QLineEdit(places_info)
            places_display.setReadOnly(True)
            layout.addRow("Places:", places_display)

        events_selection = None
        events_list = getattr(self.main_controller.project, "events", [])
        if events_list:
            if force_event_id is not None:
                forced_event = None
                for event in events_list:
                    if getattr(event, "id", None) == force_event_id:
                        forced_event = event
                        break
                forced_name = "(Unknown event)"
                if forced_event is not None and getattr(forced_event, "name", ""):
                    forced_name = forced_event.name
                events_display = QLineEdit(forced_name)
                events_display.setReadOnly(True)
                layout.addRow("Event:", events_display)
            else:
                selected_event_ids = []
                if character is not None:
                    stored_ids = getattr(character, "associated_events", [])
                    if isinstance(stored_ids, list):
                        for event_id in stored_ids:
                            selected_event_ids.append(event_id)
                events_selection = self.main_controller.ui_controller.create_relation_selection(
                    layout,
                    events_list,
                    "Events",
                    selected_event_ids,
                )

                if places_display is not None and events_selection is not None:

                    def update_places_display():
                        chosen_ids = []
                        for item in events_selection.selectedItems():
                            event_id = item.data(Qt.UserRole)
                            if event_id:
                                chosen_ids.append(event_id)
                        temp_character = Character("temp")
                        temp_character.associated_events = chosen_ids
                        new_places_info = self.main_controller.helper_controller.get_char_places(temp_character)
                        places_display.setText(new_places_info)

                    events_selection.itemSelectionChanged.connect(update_places_display)
        else:
            no_events_field = QLineEdit("No events available")
            no_events_field.setReadOnly(True)
            layout.addRow("Events:", no_events_field)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addRow(buttons)

        result: Dict[str, Any] = {}

        def on_accept():
            name = name_edit.text().strip()
            is_valid, error_msg = self.main_controller.ui_controller.validate_name_input(name, "Character name")
            if not is_valid:
                QMessageBox.warning(self.main_controller, 'Invalid Name', error_msg)
                return
            if self.main_controller.is_name_taken('character', name, getattr(character, 'id', None)):
                QMessageBox.warning(self.main_controller, 'Duplicate Name', 'A character with this name already exists. Please choose another name.')
                return
            
            selected_event_ids: List[str] = []
            if events_selection:
                for item in events_selection.selectedItems():
                    selected_event_ids.append(item.data(Qt.UserRole))
            elif force_event_id:
                selected_event_ids.append(force_event_id)
            selected_event_ids = HelperController.deduplicate_ids(selected_event_ids)
            if not self.main_controller.validation_manager.validate_char_events(selected_event_ids):
                return

            selected_place_ids: List[str] = []

            description_text = description_edit.toPlainText()
            notes_text = notes_edit.toPlainText()

            if len(description_text) > 200:
                QMessageBox.warning(self.main_controller, 'Text Too Long', 'Description must be 200 characters or less.')
                return

            if len(notes_text) > 200:
                QMessageBox.warning(self.main_controller, 'Text Too Long', 'Notes must be 200 characters or less.')
                return

            age_value = age_spin.value()
            if age_value <= 0:
                age_value = None

            result.update({
                'name': name,
                'description': description_text,
                'age': age_value,
                'notes': notes_text,
                'files': self.main_controller.ui_controller.get_files_from_list_widget(files_widget),
                'places': selected_place_ids,
                'events': selected_event_ids,
            })
            dialog.accept()

        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(dialog.reject)

        return result if dialog.exec() == QDialog.Accepted else None
