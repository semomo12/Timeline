from datetime import date
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextOption
from PySide6.QtWidgets import QComboBox,QDialog,QDialogButtonBox,QFormLayout,QInputDialog,QLineEdit,QMessageBox,QTextEdit
from core.data.event import Event
from core.logic.objects.base_controller import BaseEntityController

class EventController(BaseEntityController):
    """Basic for events."""

    def __init__(self, main_controller):
        self.main_controller = main_controller
        self._check_single_place()

    def add(self):
        form_data = self._dialog()
        if not form_data:
            return
        if self.main_controller.is_name_taken("event", form_data["name"]):
            QMessageBox.warning(self.main_controller, "Duplicate Name", "An event with this name already exists.")
            return

        new_event = Event(form_data["name"])
        self._copy_form_to_event(new_event, form_data)
        self.main_controller.project.events.append(new_event)
        self._after_event_saved(new_event, set(), set(), is_new=True)
        QMessageBox.information(self.main_controller, "Event Added", f'Event "{new_event.name}" added!\nID: {new_event.id}')

    def edit(self):
        event_to_edit = self.select_event("Edit Event", "Select event to edit:")
        if not event_to_edit:
            return
        self._edit_existing_event(event_to_edit)

    def edit_by_id(self, event_id):
        if not event_id:
            return
        event = self.get_event_by_id(event_id)
        if event:
            self._edit_existing_event(event)

    def remove(self):
        event_to_remove = self.select_event("Remove Event", "Select event to remove:")
        if not event_to_remove:
            return
        confirm = QMessageBox.question(
            self.main_controller,
            "Confirm Removal",
            f'Are you sure you want to remove event "{event_to_remove.name}"?',
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        self.main_controller.project.events.remove(event_to_remove)
        self.main_controller._maybe_unlock_timeline_modes()
        self.update_after_change()
        QMessageBox.information(self.main_controller, "Event Removed", f'Event "{event_to_remove.name}" removed!')

    def _edit_existing_event(self, event):
        form_data = self._dialog(event)
        if not form_data:
            return

        previous_participants = set(getattr(event, "participants", []))
        previous_places = set(getattr(event, "associated_places", []))

        self._copy_form_to_event(event, form_data)
        self._after_event_saved(event, previous_participants, previous_places)
        QMessageBox.information(self.main_controller, "Event Updated", f'Event "{event.name}" updated successfully!')

    def _copy_form_to_event(self, event, data):
        event.name = data["name"]
        event.description = data["description"]
        event.files = data["files"]
        event.notes = data["notes"]
        event.timeline_mode = data["timeline_mode"]
        event.display_mode = data["display_mode"]
        event.start_date = data["start_date"]
        event.end_date = data["end_date"]
        event.day_index = data["day_index"]
        event.day_index_end = data["day_index_end"]
        event.day_number = event.day_index
        event.day_number_end = event.day_index_end
        event.associated_places = self._enforce_single_place_selection(data["places"])
        event.participants = self.main_controller._deduplicate_ids(data["participants"])

    def _after_event_saved(self, event, previous_participants, previous_places, is_new=False):
        self._sync_timeline_flags(event, is_new)
        self.update_char_links(event, previous_participants)
        self.update_place_links(event, previous_places)
        self.update_after_change()

    def _sync_timeline_flags(self, event, force_mode):
        if force_mode:
            if event.timeline_mode == "day_sequence":
                self.main_controller.timeline_mode = "day_sequence"
            else:
                self.main_controller.timeline_mode = "calendar"
                
        if not self.main_controller.timeline_mode_locked:
            self.main_controller.timeline_mode_locked = True
        if not self.main_controller.timeline_display_mode_locked:
            display_mode = getattr(event, "display_mode", "span")
            if not display_mode:
                display_mode = "span"
            self.main_controller.timeline_display_mode = display_mode
            self.main_controller.timeline_display_mode_locked = True

    def update_char_links(self, event, previous_participants):
        current_participants = set(getattr(event, "participants", []))
        for character in self.main_controller.project.characters:
            if not hasattr(character, "associated_events"):
                character.associated_events = []

            if character.id in current_participants:
                self.main_controller._append_unique(character.associated_events, event.id)
                self.main_controller._update_character_places_from_events(character)
            elif character.id in previous_participants and event.id in character.associated_events:
                character.associated_events = [eid for eid in character.associated_events if eid != event.id]
                self.main_controller._update_character_places_from_events(character)

    def update_place_links(self, event, previous_places):
        current_places = set(getattr(event, "associated_places", []))
        for place in self.main_controller.project.places:
            if not hasattr(place, "associated_events"):
                place.associated_events = []

            if place.id in current_places:
                self.main_controller._append_unique(place.associated_events, event.id)
            elif place.id in previous_places and event.id in place.associated_events:
                place.associated_events = [eid for eid in place.associated_events if eid != event.id]

    def update_after_change(self):
        self.main_controller._sync_timeline_settings()
        self.main_controller.mark_project_dirty()
        self.main_controller._update_ui()


    def _dialog(self, event=None):
        dialog = QDialog(self.main_controller)
        dialog.setWindowTitle("Edit Event" if event else "Add Event")
        dialog.setMinimumWidth(500)
        layout = QFormLayout(dialog)

        existing_name = event.name if event else ""
        name_edit = QLineEdit(existing_name)

        description_edit = QTextEdit()
        description_edit.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        description_edit.setMaximumHeight(80)
        description_text = getattr(event, "description", "") if event else ""
        if description_text is None:
            description_text = ""
        if len(description_text) > 200:
            description_text = description_text[:200]
        description_edit.setPlainText(description_text)

        notes_edit = QTextEdit()
        notes_edit.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        notes_edit.setMaximumHeight(60)
        notes_text = getattr(event, "notes", "") if event else ""
        if notes_text is None:
            notes_text = ""
        if len(notes_text) > 200:
            notes_text = notes_text[:200]
        notes_edit.setPlainText(notes_text)

        layout.addRow("Name*:", name_edit)
        layout.addRow("Description:", description_edit)

        existing_files = getattr(event, "files", []) if event else []
        if existing_files is None:
            existing_files = []
        files_widget = self.main_controller.ui_controller.create_image_upload_section(layout, existing_files)

        mode_combo = QComboBox()
        mode_combo.addItem("Calendar dates", "calendar")
        mode_combo.addItem("Day sequence", "day_sequence")
        current_mode = self.main_controller.timeline_mode
        if event and getattr(event, "timeline_mode", None):
            current_mode = event.timeline_mode
        if current_mode == "day_sequence":
            mode_combo.setCurrentIndex(1)
        if self.main_controller.timeline_mode_locked:
            mode_combo.setEnabled(False)

        start_date_edit = QLineEdit()
        end_date_edit = QLineEdit()
        layout.addRow("Timeline mode:", mode_combo)
        layout.addRow("Start Date:", start_date_edit)
        layout.addRow("End Date:", end_date_edit)

        display_value = getattr(event, "display_mode", self.main_controller.timeline_display_mode)
        if display_value not in {"span", "point"}:
            display_value = "span"

        def refresh_placeholders():
            if mode_combo.currentData() == "day_sequence":
                start_date_edit.setPlaceholderText("Day 1")
                end_date_edit.setPlaceholderText("Day 1")
                start_date_edit.setText("Day 1")
                end_date_edit.setText("Day 1")
            else:
                today = date.today().isoformat()
                start_date_edit.setPlaceholderText("YYYY-MM-DD")
                end_date_edit.setPlaceholderText("YYYY-MM-DD")
                start_date_edit.setText(today)
                end_date_edit.setText(today)    

        mode_combo.currentIndexChanged.connect(lambda _: refresh_placeholders())
        refresh_placeholders()

        if event:
            start_date_edit.setText(self.format_date_value(event, is_start=True))
            end_date_edit.setText(self.format_date_value(event, is_start=False))
        else:
            if mode_combo.currentData() == "day_sequence":
                next_index = self.main_controller._next_day_index()
                start_date_edit.setText(f"Day {next_index}")
                end_date_edit.setText(f"Day {next_index}")
            else:
                today = date.today().isoformat()
                start_date_edit.setText(today)
                end_date_edit.setText(today)

        if self.main_controller.project.places:
            chosen_place_id = None
            if event and getattr(event, "associated_places", None):
                if event.associated_places:
                    chosen_place_id = event.associated_places[0]
            place_selector = self.main_controller.ui_controller.create_single_place_selection(
                layout,
                self.main_controller.project.places,
                chosen_place_id,
            )
        else:
            place_selector = None
            layout.addRow("Place:", QLineEdit("No places available"))

        if self.main_controller.project.characters:
            selected_char_ids = getattr(event, "participants", []) if event else []
            character_selector = self.main_controller.ui_controller.create_relation_selection(
                layout,
                self.main_controller.project.characters,
                "Characters",
                selected_char_ids,
            )
        else:
            character_selector = None
            layout.addRow("Characters:", QLineEdit("No characters available"))

        layout.addRow("Notes:", notes_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addRow(buttons)

        form_data = {}

        def on_accept():
            name_text = name_edit.text().strip()
            is_valid, error_message = self.main_controller.ui_controller.validate_name_input(name_text, "Event name")
            if not is_valid:
                QMessageBox.warning(self.main_controller, "Invalid Name", error_message)
                return

            if self.main_controller.is_name_taken("event", name_text, getattr(event, "id", None)):
                QMessageBox.warning(self.main_controller, "Duplicate Name", "An event with this name already exists.")
                return

            mode_value = mode_combo.currentData()
            start_text = start_date_edit.text().strip()
            end_text = end_date_edit.text().strip()

            valid_start, start_error = self.main_controller.ui_controller.validate_date_input(start_text, "Start date")
            if not valid_start:
                QMessageBox.warning(self.main_controller, "Invalid Start Date", start_error)
                return

            valid_end, end_error = self.main_controller.ui_controller.validate_date_input(end_text, "End date")
            if not valid_end:
                QMessageBox.warning(self.main_controller, "Invalid End Date", end_error)
                return

            if mode_value == "day_sequence":
                start_index = self.main_controller._parse_day_index(start_text)
                end_index = self.main_controller._parse_day_index(end_text)
                if not start_text.strip():
                    start_index = 1
                if not end_text.strip():
                    end_index = start_index or 1
                if start_index is None:
                    start_index = 1
                if end_index is None or end_index < start_index:
                    end_index = start_index

                start_value = f"Day {start_index}"
                end_value = f"Day {end_index}"
                day_index = start_index
                day_index_end = end_index

            else:
                parsed_start = self.main_controller._parse_date(start_text) or date.today()
                parsed_end = self.main_controller._parse_date(end_text) or parsed_start
                start_value = parsed_start.isoformat()
                end_value = parsed_end.isoformat()
                day_index = None
                day_index_end = None

            chosen_places = []
            if place_selector:
                place_id = place_selector.currentData()
                if place_id:
                    chosen_places.append(place_id)

            chosen_participants = []
            if character_selector:
                for item in character_selector.selectedItems():
                    chosen_participants.append(item.data(Qt.UserRole))

            chosen_participants = self.main_controller._deduplicate_ids(chosen_participants)
            chosen_places = self._enforce_single_place_selection(chosen_places)

            event_id_for_validation = getattr(event, "id", None)
            if chosen_participants and not self.main_controller._validate_event_chars(
                name_text,
                start_value,
                end_value,
                mode_value,
                day_index,
                day_index_end,
                chosen_participants,
                event_id_for_validation,
            ):
                return

            description_value = description_edit.toPlainText()
            notes_value = notes_edit.toPlainText()
            if len(description_value) > 200:
                QMessageBox.warning(self.main_controller, "Text Too Long", "Description must be 200 characters or less.")
                return
            if len(notes_value) > 200:
                QMessageBox.warning(self.main_controller, "Text Too Long", "Notes must be 200 characters or less.")
                return

            form_data["name"] = name_text
            form_data["description"] = description_value
            form_data["files"] = self.main_controller.ui_controller.get_files_from_list_widget(files_widget)
            form_data["timeline_mode"] = mode_value
            form_data["display_mode"] = display_value
            form_data["start_date"] = start_value
            form_data["end_date"] = end_value
            form_data["day_index"] = day_index
            form_data["day_index_end"] = day_index_end
            form_data["places"] = chosen_places
            form_data["participants"] = chosen_participants
            form_data["notes"] = notes_value
            dialog.accept()

        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.Accepted:
            return form_data
        return None

    def select_event(self, title, prompt):
        events = getattr(self.main_controller.project, "events", [])
        if not events:
            QMessageBox.information(self.main_controller, "No Events", "No events available.")
            return None
        items = [f"{event.name} ({event.id})" for event in events]
        selected, ok = QInputDialog.getItem(self.main_controller, title, prompt, items, 0, False)
        if not ok or not selected:
            return None
        chosen_event = None
        if "(" in selected and selected.endswith(")"):
            event_id = selected[selected.rfind("(") + 1:-1]
            for event in events:
                if event.id == event_id:
                    chosen_event = event
                    break
        if chosen_event is None:
            event_name = selected.split(" (")[0]
            for event in events:
                if event.name == event_name:
                    chosen_event = event
                    break
        if chosen_event is None:
            QMessageBox.warning(self.main_controller, "Event Not Found", "Selection failed.")
        return chosen_event

    def get_event_by_id(self, event_id):
        for event in self.main_controller.project.events:
            if getattr(event, "id", None) == event_id:
                return event
        QMessageBox.warning(
            self.main_controller,
            "Event Not Found",
            "Could not locate the selected event.",
        )
        return None

    def format_date_value(self, event, *, is_start):
        mode = getattr(event, "timeline_mode", self.main_controller.timeline_mode)
        if mode == "day_sequence":
            index = getattr(event, "day_index" if is_start else "day_index_end", None)
            if index is None:
                raw_value = getattr(event, "start_date" if is_start else "end_date", "")
                index = self.main_controller._parse_day_index(raw_value)
            return f"Day {index}" if index else ""
        return getattr(event, "start_date" if is_start else "end_date", "")

    def _check_single_place(self) -> None:
        project = getattr(self.main_controller, "project", None)
        if not project:
            return
        places = getattr(project, "places", [])
        places_by_id = {}
        for place in places:
            places_by_id[place.id] = place
        for event in getattr(project, "events", []):
            self.ensure_place(event, places_by_id)

    def ensure_place(self, event, places_by_id=None):
        raw_places = getattr(event, "associated_places", [])
        place_ids = []
        for pid in raw_places:
            if pid:
                place_ids.append(pid)
        if not place_ids:
            event.associated_places = []
            return

        primary = place_ids[0]
        event.associated_places = [primary]
        if places_by_id is None:
            places_by_id = {}
            for place in self.main_controller.project.places:
                places_by_id[place.id] = place

        primary_place = places_by_id.get(primary)
        if primary_place is not None:
            self.main_controller._append_unique(primary_place.associated_events, event.id)

        for pid in place_ids[1:]:
            place = places_by_id.get(pid)
            if place and hasattr(place, "associated_events"):
                place.associated_events = [eid for eid in place.associated_events if eid != event.id]

    def _enforce_single_place_selection(self, place_ids):
        if not place_ids:
            return []
        unique_ids = self.main_controller._deduplicate_ids(place_ids)
        filtered_ids = []
        for pid in unique_ids:
            if pid:
                filtered_ids.append(pid)
        if filtered_ids:
            return [filtered_ids[0]]
        return []

    def resolve_place(self, event, lane_map):
        """which place an event should appear in"""
        for place_id in getattr(event, "associated_places", []):
            if place_id in lane_map:
                return place_id
        return "__NO_PLACE__"
