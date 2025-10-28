from PySide6.QtWidgets import QMessageBox, QInputDialog, QDialog, QFormLayout, QLineEdit, QTextEdit, QDialogButtonBox
from PySide6.QtGui import QTextOption
from core.data.place import Place
from core.utils.timeline_helpers import HelperController
from core.logic.objects.base_controller import BaseEntityController

class PlaceController(BaseEntityController):
    """Manages place operations"""

    def __init__(self, main_controller):
        self.main_controller = main_controller

    def add(self):
        """Add new place"""
        dialog_data = self._dialog()
        if not dialog_data:
            return
        if self.main_controller.is_name_taken('place', dialog_data['name']):
            QMessageBox.warning(self.main_controller, 'Duplicate Name', 'A place with this name already exists. Please choose another name.')
            return

        new_place = Place(dialog_data['name'])
        new_place.description = dialog_data['description']
        new_place.files = dialog_data['files']
        new_place.parent_location = dialog_data['location']
        new_place.notes = dialog_data['notes']
        new_place.associated_characters = HelperController.deduplicate_ids(dialog_data['characters'])
        new_place.associated_events = HelperController.deduplicate_ids(dialog_data['events'])

        self.main_controller.project.places.append(new_place)
        self.main_controller.mark_dirty()
        self.main_controller._update_ui()
        QMessageBox.information(self.main_controller, 'Place Added', f'Place "{new_place.name}" added!\n ID: {new_place.id}')

    def edit(self):
        """Edit existing place"""
        places = self.main_controller.project.places
        if not places:
            QMessageBox.information(self.main_controller, 'No Places', 'No places available to edit!')
            return

        items = [f"{place.name} ({place.id})" for place in places]
        selected_item, ok = QInputDialog.getItem(
            self.main_controller, 'Edit Place', 'Select place to edit:',
            items, 0, False
        )
        if not ok or not selected_item:
            return

        chosen_place = None
        if '(' in selected_item and selected_item.endswith(')'):
            place_id = selected_item[selected_item.rfind('(') + 1:-1]
            for candidate in places:
                if candidate.id == place_id:
                    chosen_place = candidate
                    break
        if chosen_place is None:
            selected_name = selected_item.split(' (')[0]
            for candidate in places:
                if candidate.name == selected_name:
                    chosen_place = candidate
                    break
        if chosen_place is None:
            QMessageBox.warning(self.main_controller, 'Place Not Found', 'Could not locate the selected place.')
            return

        dialog_data = self._dialog(chosen_place)
        if not dialog_data:
            return

        chosen_place.name = dialog_data['name']
        chosen_place.description = dialog_data['description']
        chosen_place.files = dialog_data['files']
        chosen_place.parent_location = dialog_data['location']
        chosen_place.notes = dialog_data['notes']
        chosen_place.associated_characters = HelperController.deduplicate_ids(dialog_data['characters'])
        chosen_place.associated_events = HelperController.deduplicate_ids(dialog_data['events'])

        self.main_controller.mark_dirty()
        self.main_controller._update_ui()
        QMessageBox.information(self.main_controller, 'Place Updated', f'Place "{chosen_place.name}" updated successfully!')

    def edit_by_id(self, place_id):
        """Edit place by id"""
        place = None
        for candidate in self.main_controller.project.places:
            if getattr(candidate, 'id', None) == place_id:
                place = candidate
                break
        if place is None:
            QMessageBox.warning(self.main_controller, 'Place Not Found', 'Could not locate the selected place.')
            return
        dialog_data = self._dialog(place)
        if not dialog_data:
            return
        place.name = dialog_data['name']
        place.description = dialog_data['description']
        place.files = dialog_data['files']
        place.parent_location = dialog_data['location']
        place.notes = dialog_data['notes']
        place.associated_characters = HelperController.deduplicate_ids(dialog_data['characters'])
        place.associated_events = HelperController.deduplicate_ids(dialog_data['events'])
        self.main_controller.mark_dirty()
        self.main_controller._update_ui()
        QMessageBox.information(self.main_controller, 'Place Updated', f'Place "{place.name}" updated successfully!')

    def remove(self):
        """Remove a place with selection dialog"""
        places = self.main_controller.project.places
        if not places:
            QMessageBox.information(self.main_controller, 'No Places', 'No places to remove!')
            return

        place_items = [f"{place.name} ({place.id})" for place in places]
        selected_item, ok = QInputDialog.getItem(
            self.main_controller, 'Remove Place', 'Select place to remove:',
            place_items, 0, False
        )

        if not ok or not selected_item:
            return

        place_name = selected_item.split(' (')[0]
        place_to_remove = None
        for place in places:
            if place.name == place_name:
                place_to_remove = place
                break
        if place_to_remove is None:
            return

        reply = QMessageBox.question(
            self.main_controller, 'Confirm Removal',
            f'Are you sure you want to remove place "{place_name}"?',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            places.remove(place_to_remove)
            self.main_controller.mark_dirty()
            self.main_controller._update_ui()
            QMessageBox.information(self.main_controller, 'Place Removed', f'Place "{place_name}" removed!')

    def _dialog(self, place=None):
        """Show place add/edit dialog"""
        dialog = QDialog(self.main_controller)
        dialog.setWindowTitle("Edit Place" if place else "Add Place")
        dialog.setMinimumWidth(500)
        layout = QFormLayout(dialog)

        name_edit = QLineEdit(place.name if place else "")

        description_edit = QTextEdit()
        description_edit.setMaximumHeight(80)
        description_edit.setMinimumHeight(60)
        description_edit.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        description_text = getattr(place, 'description', '') if place else ''
        if description_text is None:
            description_text = ''
        if len(description_text) > 200:
            description_text = description_text[:150]
        description_edit.setPlainText(description_text)

        notes_edit = QTextEdit()
        notes_edit.setMaximumHeight(60)
        notes_edit.setMinimumHeight(40)
        notes_edit.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        notes_text = getattr(place, 'notes', '') if place else ''
        if notes_text is None:
            notes_text = ''
        if len(notes_text) > 200:
            notes_text = notes_text[:150]
        notes_edit.setPlainText(notes_text)

        layout.addRow("Name*:", name_edit)
        layout.addRow("Description:", description_edit)

        existing_files = getattr(place, 'files', []) if place else []
        if existing_files is None:
            existing_files = []
        files_widget = self.main_controller.ui_controller.create_image_upload_section(layout, existing_files)
        
            # show characters in events at this place
        place_id = place.id if place else ""
        characters_in_events = self.main_controller.helper_controller.get_place_chars(place_id)
        character_names = []
        project = getattr(self.main_controller, 'project', None)
        if project and getattr(project, 'characters', None):
            id_to_name = {char.id: getattr(char, 'name', char.id) for char in project.characters}
            for character_id in characters_in_events or []:
                character_names.append(id_to_name.get(character_id, character_id))
        characters_text = ", ".join(character_names) if character_names else "No characters participate in events at this place"

        characters_display = QTextEdit()
        characters_display.setPlainText(characters_text)
        characters_display.setReadOnly(True)
        characters_display.setMaximumHeight(60)
        characters_display.setMinimumHeight(40)
        characters_display.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        layout.addRow("Characters:", characters_display)

        associated_events = getattr(place, 'associated_events', []) if place else []
        if associated_events is None:
            associated_events = []
        self.main_controller.ui_controller.create_readonly_relation_display(layout, "Events", self.main_controller.project.events, associated_events)

        layout.addRow("Notes:", notes_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addRow(buttons)

        form_data = {}

        def on_accept():
            name_text = name_edit.text().strip()

            is_valid, error_msg = self.main_controller.ui_controller.validate_name_input(name_text, "Place name")
            if not is_valid:
                QMessageBox.warning(self.main_controller, 'Invalid Name', error_msg)
                return

            current_place_id = getattr(place, 'id', None)
            if self.main_controller.is_name_taken('place', name_text, current_place_id):
                QMessageBox.warning(self.main_controller, 'Duplicate Name', 'A place with this name already exists. Please choose another name.')
                return

            existing_character_ids = getattr(place, 'associated_characters', []) if place else []
            existing_event_ids = getattr(place, 'associated_events', []) if place else []
            if existing_character_ids is None:
                existing_character_ids = []
            if existing_event_ids is None:
                existing_event_ids = []

            description_value = description_edit.toPlainText()
            notes_value = notes_edit.toPlainText()

            if len(description_value) > 200:
                QMessageBox.warning(self.main_controller, 'Text Too Long', 'Description must be 200 characters or less.')
                return

            if len(notes_value) > 200:
                QMessageBox.warning(self.main_controller, 'Text Too Long', 'Notes must be 200 characters or less.')
                return

            existing_location = getattr(place, 'parent_location', '') if place else ''
            if existing_location is None:
                existing_location = ''
            form_data['name'] = name_text
            form_data['description'] = description_value
            form_data['files'] = self.main_controller.ui_controller.get_files_from_list_widget(files_widget)
            form_data['location'] = existing_location
            form_data['notes'] = notes_value
            form_data['characters'] = existing_character_ids
            form_data['events'] = existing_event_ids
            dialog.accept()

        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(dialog.reject)

        return form_data if dialog.exec() == QDialog.Accepted else None
