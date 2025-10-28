import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import QDialog,QDialogButtonBox,QFormLayout,QHBoxLayout,QLabel,QVBoxLayout,QWidget

class TimelineInfoDialogs:
    """Shows information dialogs for timeline objects"""

    def __init__(self, timeline_controller):
        self.timeline_controller = timeline_controller
        self.main_controller = timeline_controller.main_controller

    def show_event(self, event):
        places = self.timeline_controller.data_manager.get_place_names(getattr(event, 'associated_places', []))
        participants = self.timeline_controller.data_manager.get_character_names(getattr(event, 'participants', []))
        notes = getattr(event, 'notes', '')
        images = self.get_image_paths(getattr(event, 'files', []))
        rows = [
            ("Name", event.name),
            ("Description", getattr(event, 'description', '')),
            ("Start", getattr(event, 'start_date', '')),
            ("End", getattr(event, 'end_date', '')),
            ("Places", ", ".join(places) if places else "—"),
            ("Participants", ", ".join(participants) if participants else "—"),
            ("Images", {"type": "images", "paths": images, "raw": getattr(event, 'files', [])}),
            ("Notes", notes),
        ]
        self.show_dialog(f"Event: {event.name}", rows)

    def show_char(self, character):
        places = self.timeline_controller.data_manager.get_place_names(getattr(character, 'associated_places', []))
        events = self.timeline_controller.data_manager.get_event_names(getattr(character, 'associated_events', []))
        images = self.get_image_paths(getattr(character, 'files', []))
        age = getattr(character, 'age', None)
        rows = [
            ("Name", character.name),
            ("Description", getattr(character, 'description', '')),
            ("Age", str(age) if age is not None else "—"),
            ("Color", {"type": "color", "value": getattr(character, 'color', '')}),
            ("Places", ", ".join(places) if places else "—"),
            ("Events", ", ".join(events) if events else "—"),
            ("Images", {"type": "images", "paths": images, "raw": getattr(character, 'files', [])}),
            ("Notes", getattr(character, 'notes', '')),
        ]
        self.show_dialog(f"Character: {character.name}", rows)

    def show_place(self, place):
        characters = self.timeline_controller._place_chars(place.id)
        color = self.timeline_controller.color_manager.place_color(place.id)
        images = self.get_image_paths(getattr(place, 'files', []))
        events = self.timeline_controller.data_manager.get_event_names(getattr(place, 'associated_events', []))
        rows = [
            ("Name", place.name),
            ("Description", getattr(place, 'description', '')),
            ("Color", {"type": "color", "value": color.name() if color else ""}),
            ("Characters", ", ".join(characters) if characters else "—"),
            ("Events", ", ".join(events) if events else "—"),
            ("Images", {"type": "images", "paths": images, "raw": getattr(place, 'files', [])}),
            ("Notes", getattr(place, 'notes', '')),
        ]
        self.show_dialog(f"Place: {place.name}", rows)

    def show_dialog(self, title, rows):
        dialog = QDialog(self.main_controller)
        dialog.setWindowTitle(title)
        main_layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()
        for label, value in rows:
            label_widget = QLabel(label)
            label_widget.setStyleSheet("font-weight: bold;")
            if isinstance(value, dict):
                if value.get("type") == "color":
                    color_code = value.get("value", "")
                    color = QColor(color_code)
                    if color.isValid():
                        color_box = QLabel("")
                        color_box.setMinimumSize(80, 24)
                        color_box.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #555555;")
                        color_box.setToolTip(color.name())
                        form_layout.addRow(label_widget, color_box)
                        continue
                    value = color_code
                elif value.get("type") == "images":
                    paths = value.get("paths", [])
                    raw = value.get("raw", paths)
                    image_widget = self.image_preview(paths)
                    if image_widget:
                        form_layout.addRow(label_widget, image_widget)
                        continue
                    value = self.format_files(raw)

            value_text = self.format_value(value)
            if label.lower() in ['description', 'notes']:
                value_text = self.truncate_text(value_text, 200)
                value_text = self.wrap_text(value_text)
            value_label = QLabel(value_text)
            value_label.setWordWrap(True)
            if label.lower() in ['description', 'notes']:
                value_label.setMaximumHeight(120)
                value_label.setMinimumWidth(400)
            form_layout.addRow(label_widget, value_label)
        main_layout.addLayout(form_layout)
        ok_button = QDialogButtonBox(QDialogButtonBox.Ok)
        ok_button.accepted.connect(dialog.accept)
        main_layout.addWidget(ok_button)
        dialog.exec()

    def image_preview(self, paths):
        valid_paths = []
        for path in paths:
            if path and os.path.exists(path):
                valid_paths.append(path)
        if not valid_paths:
            return None

        class SimpleImageLabel(QLabel):
            def __init__(self, image_path, parent=None):
                super().__init__(parent)
                self.image_path = image_path
                
            def mousePressEvent(self, event):
                self.show_image_dialog()

            def show_image_dialog(self):
                dlg = QDialog(self)
                dlg.setWindowTitle(os.path.basename(self.image_path))
                vbox = QVBoxLayout(dlg)
                pixmap = QPixmap(self.image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    img_label = QLabel()
                    img_label.setPixmap(scaled_pixmap)
                    img_label.setAlignment(Qt.AlignCenter)
                    vbox.addWidget(img_label)
                ok_btn = QDialogButtonBox(QDialogButtonBox.Ok)
                ok_btn.accepted.connect(dlg.accept)
                vbox.addWidget(ok_btn)
                dlg.exec()

        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        for path in valid_paths[:3]:
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                thumb = pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                label = SimpleImageLabel(path)
                label.setPixmap(thumb)
                label.setFixedSize(64, 64)
                label.setStyleSheet("border: 1px solid #ccc; padding: 2px;")
                label.setToolTip(f"Click to view: {os.path.basename(path)}")
                layout.addWidget(label)
        if len(valid_paths) > 3:
            more_label = QLabel(f"+{len(valid_paths) - 3} more")
            more_label.setStyleSheet("color: #666; font-style: italic;")
            layout.addWidget(more_label)
        layout.addStretch()
        return widget

    def get_image_paths(self, files):
        paths = []
        for path in files or []:
            if not path:
                continue
            text = str(path)
            if os.path.exists(text):
                paths.append(text)
        return paths

    def format_files(self, files):
        if not files:
            return "—"
        file_names = [os.path.basename(str(f)) for f in files if f]
        if not file_names:
            return "—"
        return ", ".join(file_names)

    def format_value(self, value):
        if value is None or value == "":
            return "—"
        return str(value)

    def truncate_text(self, text, max_length=200):
        if not text or len(text) <= max_length:
            return text
        return text[:max_length] + "..."

    def wrap_text(self, text, words_per_line=6):
        if not text:
            return text
        lines = []
        for paragraph in text.splitlines():
            words = paragraph.split()
            for i in range(0, len(words), words_per_line):
                line = " ".join(words[i:i + words_per_line])
                lines.append(line)
        return "\n".join(lines)
