from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtWidgets import QHeaderView,QLabel,QHBoxLayout,QWidget,QTableWidgetItem,QMessageBox
import os
from datetime import datetime
from typing import List

class FilePreviewLabel(QLabel):
    """Clickable label that shows image"""

    def __init__(self, file_path, preview):
        super().__init__()
        self._file_path = file_path
        self.setAlignment(Qt.AlignCenter)
        self.setPixmap(preview)
        self.setToolTip(file_path)
        self.setCursor(Qt.PointingHandCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._file_path:
            self.show_image_dialog()
        super().mouseReleaseEvent(event)

    def show_image_dialog(self):
        from PySide6.QtWidgets import QDialog, QVBoxLayout
        dlg = QDialog(self)
        dlg.setWindowTitle(os.path.basename(self._file_path))
        vbox = QVBoxLayout(dlg)
        pixmap = QPixmap(self._file_path)
        label = QLabel()
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
        vbox.addWidget(label)
        dlg.resize(min(900, pixmap.width()+40), min(700, pixmap.height()+80))
        dlg.exec()

class TableController:
    """Controller for table views"""

    def __init__(self, main_controller):
        self.main_controller = main_controller
        self._preview_size = QSize(96, 96)
        self._signals_attached = False
        self._updating_tables = False

    def update_tables(self):
        """Refresh every table."""
        previous = self._updating_tables
        self._updating_tables = True
        try:
            self._update_places_table()
            self._update_characters_table()
            self._update_events_table()
        finally:
            self._updating_tables = previous

    def attach_table_signals(self):
        """Connect table edit signals to controller."""
        if self._signals_attached:
            return

        table = getattr(self.main_controller, 'tablePlacesData', None)
        if table:
            table.itemChanged.connect(self._on_place_item_changed)

        table = getattr(self.main_controller, 'tableCharactersData', None)
        if table:
            table.itemChanged.connect(self.on_char_itm_changed)

        table = getattr(self.main_controller, 'tableEventsData', None)
        if table:
            table.itemChanged.connect(self._on_event_item_changed)

        self._signals_attached = True

    def _update_places_table(self):
        if not hasattr(self.main_controller, 'tablePlacesData') or not self.main_controller.tablePlacesData:
            return

        table = self.main_controller.tablePlacesData
        places = self.main_controller.project.places

        headers = [
            "ID",
            "Created",
            "Name",
            "Description",
            "Files",
            "Events",
            "Characters",
            "Notes",
        ]
        table.blockSignals(True)
        try:
            self._prepare_table(table, headers)
            table.setRowCount(len(places))

            for row, place in enumerate(places):
                id_item = QTableWidgetItem(place.id)
                id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 0, id_item)

                created_text = self._format_created(place.created)
                created_item = QTableWidgetItem(created_text)
                created_item.setFlags(created_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 1, created_item)

                self._set_text_item(table, row, 2, place.name, editable=True)
                self._set_description_or_notes_item(table, row, 3, place.description, editable=True)
                self._set_file_cell(table, row, 4, place.files)

                event_names = []
                for event_id in place.associated_events:
                    event_names.append(self._get_event_name(event_id))
                events_text = ", ".join(event_names)

                character_ids = self.main_controller.helper_controller.get_place_chars(place.id)
                character_names = []
                if character_ids:
                    for character_id in character_ids:
                        character_names.append(self._get_character_name(character_id))
                characters_text = ", ".join(character_names) if character_names else ""

                self._set_text_item(table, row, 5, events_text, editable=False)
                self._set_text_item(table, row, 6, characters_text, editable=False)
                self._set_description_or_notes_item(table, row, 7, place.notes, editable=True)

            self.setup_table(table)
        finally:
            table.blockSignals(False)

    def _update_characters_table(self):
        if not hasattr(self.main_controller, 'tableCharactersData') or not self.main_controller.tableCharactersData:
            return

        table = self.main_controller.tableCharactersData
        characters = self.main_controller.project.characters

        headers = [
            "ID",
            "Created",
            "Name",
            "Age",
            "Description",
            "Files",
            "Events",
            "Places",
            "Notes",
        ]
        table.blockSignals(True)
        try:
            self._prepare_table(table, headers)
            table.setRowCount(len(characters))

            for row, character in enumerate(characters):
                id_item = QTableWidgetItem(character.id)
                id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 0, id_item)

                created_text = self._format_created(character.created)
                created_item = QTableWidgetItem(created_text)
                created_item.setFlags(created_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 1, created_item)

                self._set_text_item(table, row, 2, character.name, background=character.color, editable=True)
                age_text = str(character.age) if getattr(character, 'age', None) is not None else ""
                self._set_text_item(table, row, 3, age_text, editable=False)
                self._set_description_or_notes_item(table, row, 4, character.description, editable=True)
                self._set_file_cell(table, row, 5, character.files)

                event_names = []
                for event_id in character.associated_events:
                    event_names.append(self._get_event_name(event_id))
                events_text = ", ".join(event_names)

                place_names = []
                for place_id in character.associated_places:
                    place_names.append(self._get_place_name(place_id))
                places_text = ", ".join(place_names)

                self._set_text_item(table, row, 6, events_text, editable=False)
                self._set_text_item(table, row, 7, places_text, editable=False)
                self._set_description_or_notes_item(table, row, 8, character.notes, editable=True)

            self.setup_table(table)
        finally:
            table.blockSignals(False)

    def _update_events_table(self):
        if not hasattr(self.main_controller, 'tableEventsData') or not self.main_controller.tableEventsData:
            return

        table = self.main_controller.tableEventsData
        events = self.main_controller.project.events

        headers = [
            "ID",
            "Created",
            "Name",
            "Start Date",
            "End Date",
            "Description",
            "Files",
            "Places",
            "Characters",
            "Notes",
        ]
        table.blockSignals(True)
        try:
            self._prepare_table(table, headers)
            table.setRowCount(len(events))

            for row, event in enumerate(events):
                id_item = QTableWidgetItem(event.id)
                id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 0, id_item)

                created_text = self._format_created(event.created)
                created_item = QTableWidgetItem(created_text)
                created_item.setFlags(created_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 1, created_item)

                self._set_text_item(table, row, 2, event.name, editable=True)
                self._set_text_item(table, row, 3, event.start_date, editable=True)
                self._set_text_item(table, row, 4, event.end_date, editable=True)
                self._set_description_or_notes_item(table, row, 5, event.description, editable=True)
                self._set_file_cell(table, row, 6, event.files)

                character_names = []
                for char_id in event.participants:
                    character_names.append(self._get_character_name(char_id))
                characters_text = ", ".join(character_names)

                place_names = []
                for place_id in event.associated_places:
                    place_names.append(self._get_place_name(place_id))
                places_text = ", ".join(place_names)

                self._set_text_item(table, row, 7, places_text, editable=False)
                self._set_text_item(table, row, 8, characters_text, editable=False)
                self._set_description_or_notes_item(table, row, 9, event.notes, editable=True)

            self.setup_table(table)
        finally:
            table.blockSignals(False)

    def _format_created(self, value):
        """Return a YYYY-MM-DD string """
        if not value:
            return ""
        if isinstance(value, str):
            return value[:10]
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")
        try:
            return str(value)[:10]
        except Exception:
            return ""

    def _get_character_name(self, character_id):
        """by ID"""
        for character in self.main_controller.project.characters:
            if character.id == character_id:
                return character.name
        return f"Unknown ({character_id})"

    def _get_event_name(self, event_id):
        """by ID"""
        for event in self.main_controller.project.events:
            if event.id == event_id:
                return event.name
        return f"Unknown ({event_id})"

    def _get_place_name(self, place_id):
        """by ID"""
        for place in self.main_controller.project.places:
            if place.id == place_id:
                return place.name
        return f"Unknown ({place_id})"

    def _prepare_table(self, table, headers):
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setWordWrap(True)

    def setup_table(self, table):
        header = table.horizontalHeader()
        for col in range(table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)
        vertical_header = table.verticalHeader()
        if vertical_header:
            vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()

    def _set_file_cell(self, table, row, column, files):
        table.removeCellWidget(row, column)

        file_list: List[str] = []
        for path in files:
            if path:
                file_list.append(path)

        if file_list:
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(4)

            previews_added = 0
            max_previews = 3

            for file_path in file_list:
                if not os.path.exists(file_path):
                    continue

                pixmap = QPixmap(file_path)
                if pixmap.isNull():
                    continue

                preview = pixmap.scaled(
                    self._preview_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                label = FilePreviewLabel(file_path, preview)
                label.setMinimumSize(preview.size())
                layout.addWidget(label)
                previews_added += 1

                if previews_added >= max_previews:
                    break

            if previews_added:
                layout.addStretch(1)
                table.setCellWidget(row, column, container)

        display_name_parts = []
        for path in file_list:
            display_name_parts.append(os.path.basename(path))
        display_names = ", ".join(display_name_parts)
        tooltip = "\n".join(file_list)

        item_text = self._wrap_text(display_names)
        item = QTableWidgetItem(item_text)
        if tooltip:
            item.setToolTip(tooltip)
        item.setData(Qt.UserRole, file_list)
        table.setItem(row, column, item)

    def _on_place_item_changed(self, item):
        table, identifier = self._prepare_change(item, {2, 4, 8})
        if not identifier:
            return
        place = self._lookup_place(identifier)
        if not place:
            return

        value = self._clean_text(item.text())
        if item.column() == 2:
            if self.main_controller.is_name_taken('place', value, place.id):
                QMessageBox.warning(self.main_controller, 'Duplicate Name', 'A place with this name already exists. Please choose another name.')
                self._restore_item_text(item, place.name)
                return
            place.name = value
        elif item.column() == 3:
            place.description = value
        elif item.column() == 7:
            place.notes = value
        else:
            return
        self._post_edit_refresh(table, item.row(), item.column())

    def on_char_itm_changed(self, item):
        table, identifier = self._prepare_change(item, {2, 3, 7})
        if not identifier:
            return
        character = self._lookup_character(identifier)
        if not character:
            return

        value = self._clean_text(item.text())
        column = item.column()
        if column == 2:
            if self.main_controller.is_name_taken('character', value, character.id):
                QMessageBox.warning(self.main_controller, 'Duplicate Name', 'A character with this name already exists. Please choose another name.')
                self._restore_item_text(item, character.name)
                return
            character.name = value
        elif column == 4:
            character.description = value
        elif column == 8:
            character.notes = value
        else:
            return
        self._post_edit_refresh(table, item.row(), item.column())

    def _on_event_item_changed(self, item):
        table, identifier = self._prepare_change(item, {2, 3, 4, 5, 9})
        if not identifier:
            return
        event = self._lookup_event(identifier)
        if not event:
            return

        value = self._clean_text(item.text())
        column = item.column()
        if column == 2:
            if self.main_controller.is_name_taken('event', value, event.id):
                QMessageBox.warning(self.main_controller, 'Duplicate Name', 'An event with this name already exists. Please choose another name.')
                self._restore_item_text(item, event.name)
                return
            event.name = value
        elif column == 3:
            event.start_date = value
        elif column == 4:
            event.end_date = value
        elif column == 5:
            event.description = value
        elif column == 9:
            event.notes = value
        else:
            return
        self._post_edit_refresh(table, item.row(), item.column())

    def _set_text_item(self, table, row, column, text, background= None, editable= True):
        original = text or ""
        wrapped = self._wrap_text(original)
        item = QTableWidgetItem(wrapped)
        item.setData(Qt.UserRole, original)
        tooltip_lines: List[str] = []
        if original and original != wrapped:
            tooltip_lines.append(original)
        if background:
            color = QColor(background)
            if color.isValid():
                item.setBackground(color)
                item.setForeground(self._pick_text_color(color))
                tooltip_lines.append(f"Color: {color.name()}")
        if tooltip_lines:
            item.setToolTip("\n".join(tooltip_lines))
        if not editable:
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        else:
            item.setFlags(item.flags() | Qt.ItemIsEditable)
        table.setItem(row, column, item)

    def _truncate(self, text, max_length= 200):
        """Truncate text to max length"""
        if not text or len(text) <= max_length:
            return text
        return text[:max_length]

    def _set_description_or_notes_item(self, table, row, column, text, background= None, editable= True):
        """wrap escription and notes to 6-words-per-line"""
        
        original = text or ""
        truncated = self._truncate(original, 200)
        wrapped = self._wrap_text(truncated, words_per_line=6)  # Use 6 words per line for better readability
        item = QTableWidgetItem(wrapped)
        item.setData(Qt.UserRole, original)
        tooltip_lines: List[str] = []
        if original and original != wrapped:
            tooltip_lines.append(original)
        if background:
            color = QColor(background)
            if color.isValid():
                item.setBackground(color)
                item.setForeground(self._pick_text_color(color))
                tooltip_lines.append(f"Color: {color.name()}")
        if tooltip_lines:
            item.setToolTip("\n".join(tooltip_lines))
        if not editable:
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        else:
            item.setFlags(item.flags() | Qt.ItemIsEditable)
        table.setItem(row, column, item)

    def _wrap_text(self, text, words_per_line= 6):
        if not text:
            return ""
        lines: List[str] = []
        for paragraph in text.splitlines():
            words = paragraph.split()
            if not words:
                lines.append("")
                continue
            for i in range(0, len(words), words_per_line):
                lines.append(" ".join(words[i:i + words_per_line]))
        return "\n".join(lines)

    def _pick_text_color(self, color):
        brightness = (
            color.red() * 299
            + color.green() * 587
            + color.blue() * 114
        ) / 1000
        if brightness > 186:
            return QColor("black")
        return QColor("white")

    def _restore_item_text(self, item, text):
        table = item.tableWidget()
        if not table:
            return
        table.blockSignals(True)
        previous = self._updating_tables
        try:
            self._updating_tables = True
            item.setText(text)
            item.setData(Qt.UserRole, text)
        finally:
            self._updating_tables = previous
            table.blockSignals(False)

    def _prepare_change(self, item, allowed_columns):
        if item is None or self._updating_tables:
            return None, None
        table = item.tableWidget()
        if table is None or item.column() not in allowed_columns:
            return None, None
        identifier = self.row_indentify(table, item.row())
        if not identifier:
            return None, None
        return table, identifier

    def row_indentify(self, table, row):
        id_item = table.item(row, 0)
        if not id_item:
            return ""
        return (id_item.text() or "").strip()

    def _lookup_place(self, place_id):
        for place in self.main_controller.project.places:
            if place.id == place_id:
                return place
        return None

    def _lookup_character(self, character_id):
        for character in self.main_controller.project.characters:
            if character.id == character_id:
                return character
        return None

    def _lookup_event(self, event_id):
        for event in self.main_controller.project.events:
            if event.id == event_id:
                return event
        return None

    def _clean_text(self, value):
        return (value or "").strip()

    def _post_edit_refresh(self, table=None, row= None, column= None):
        self.update_tables()
        if table is not None and row is not None and column is not None:
            try:
                if 0 <= row < table.rowCount() and 0 <= column < table.columnCount():
                    table.setCurrentCell(row, column)
            except Exception:
                pass
        if hasattr(self.main_controller, 'timeline_controller') and self.main_controller.timeline_controller:
            self.main_controller.timeline_controller.update_timeline()
        if hasattr(self.main_controller, 'mark_project_dirty'):
            self.main_controller.mark_project_dirty()
