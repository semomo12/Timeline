import os
import re
from PySide6.QtGui import QTextOption
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QGraphicsView,QTableWidget, QPushButton, 
    QListWidget, QListWidgetItem, QFileDialog,QMessageBox, QLineEdit, QTextEdit,QComboBox
)

class UIController:
    """Manages UI"""

    def __init__(self, main_controller):
        self.main_controller = main_controller

    def create_basic_ui(self):
        """Create UI if .ui file is missing or loading fails."""
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        #Timeline and Table buttons
        second_row_layout = QHBoxLayout()
        second_row_layout.addStretch()
        self.main_controller.btnTimeline = QPushButton("▦")
        self.main_controller.btnTable = QPushButton("⚏")
        second_row_layout.addWidget(self.main_controller.btnTimeline)
        second_row_layout.addWidget(self.main_controller.btnTable)
        second_row_layout.addStretch()
        layout.addLayout(second_row_layout)

        self.main_controller.stackMain = QStackedWidget()
        layout.addWidget(self.main_controller.stackMain)

        # Timeline page
        timeline_page = QWidget()
        timeline_layout = QVBoxLayout(timeline_page)
        self.main_controller.listPlaces = None
        self.main_controller.viewTimeline = QGraphicsView()
        timeline_layout.addWidget(self.main_controller.viewTimeline)

        #Zoom buttons
        zoom_layout = QHBoxLayout()
        zoom_layout.addStretch()
        self.main_controller.btnZoomOut = QPushButton("-")
        self.main_controller.btnZoomIn = QPushButton("+")
        zoom_layout.addWidget(self.main_controller.btnZoomOut)
        zoom_layout.addWidget(self.main_controller.btnZoomIn)
        zoom_layout.addStretch()
        timeline_layout.addLayout(zoom_layout)

        self.main_controller.stackMain.addWidget(timeline_page)

        # Table page
        table_page = QWidget()
        table_layout = QVBoxLayout(table_page)

        # Table buttons
        table_buttons_layout = QHBoxLayout()
        table_buttons_layout.addStretch()
        self.main_controller.btnTablePlaces = QPushButton("Places")
        self.main_controller.btnTableCharacters = QPushButton("Characters")
        self.main_controller.btnTableEvents = QPushButton("Events")
        table_buttons_layout.addWidget(self.main_controller.btnTableEvents)
        table_buttons_layout.addWidget(self.main_controller.btnTablePlaces)
        table_buttons_layout.addWidget(self.main_controller.btnTableCharacters)
        table_buttons_layout.addStretch()
        table_layout.addLayout(table_buttons_layout)

        self.main_controller.stackTables = QStackedWidget()
        table_layout.addWidget(self.main_controller.stackTables)

        #Places table
        places_table_widget = QWidget()
        places_layout = QVBoxLayout(places_table_widget)
        self.main_controller.tablePlacesData = QTableWidget(0, 8)
        self.main_controller.tablePlacesData.setHorizontalHeaderLabels(["ID", "Created", "Name", "Description", "Files", "Events", "Characters", "Notes"])
        places_layout.addWidget(self.main_controller.tablePlacesData)
        self.main_controller.stackTables.addWidget(places_table_widget)

        #Characters table
        characters_table_widget = QWidget()
        characters_layout = QVBoxLayout(characters_table_widget)
        self.main_controller.tableCharactersData = QTableWidget(0, 8)
        self.main_controller.tableCharactersData.setHorizontalHeaderLabels(["ID", "Created", "Name", "Description", "Files", "Events", "Places", "Notes"])
        characters_layout.addWidget(self.main_controller.tableCharactersData)
        self.main_controller.stackTables.addWidget(characters_table_widget)

        #Events table
        events_table_widget = QWidget()
        events_layout = QVBoxLayout(events_table_widget)
        self.main_controller.tableEventsData = QTableWidget(0, 10)
        self.main_controller.tableEventsData.setHorizontalHeaderLabels([
            "ID", "Created", "Name", "Start Date", "End Date",
            "Description", "Files", "Places", "Characters", "Notes"
        ])
        events_layout.addWidget(self.main_controller.tableEventsData)
        self.main_controller.stackTables.addWidget(events_table_widget)

        self.main_controller.stackMain.addWidget(table_page)
        self.main_controller.setCentralWidget(central_widget)
        self.main_controller.resize(1100, 700)

    def update_ui(self):
        """Update UI elements"""
        self.main_controller._update_window_title()
        
        if hasattr(self.main_controller, 'tablePlacesData') and self.main_controller.tablePlacesData:
            self.main_controller.table_controller.update_tables()
        if hasattr(self.main_controller, 'viewTimeline') and self.main_controller.viewTimeline:
            self.main_controller.timeline_controller.update_timeline()

        self.main_controller._sync_timeline_settings()

    def create_image_upload_section(self, layout, current_files=None):
        """Create file upload section that supports multiple images."""
        current_files = current_files or []

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(6)

        file_list = QListWidget()
        file_list.setSelectionMode(QListWidget.SingleSelection)
        container_layout.addWidget(file_list)

        buttons_layout = QHBoxLayout()
        add_btn = QPushButton("Add Files")
        remove_btn = QPushButton("Remove Selected")
        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(remove_btn)
        buttons_layout.addStretch(1)
        container_layout.addLayout(buttons_layout)

        layout.addRow("Files:", container)

        for path in current_files:
            self._add_file_to_list_widget(file_list, path)

        add_btn.clicked.connect(lambda: self._upload_images(file_list))
        remove_btn.clicked.connect(lambda: self.delete_selected(file_list))
        return file_list

    def _upload_images(self, file_list):
        """manage adding one or several files."""
        dialog = QFileDialog(self.main_controller)
        dialog.setWindowTitle('Select Files')
        dialog.setNameFilter('Image Files (*.png *.jpg *.jpeg *.gif *.bmp *.webp *.tif *.tiff);;All Files (*)')
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setModal(True)
        dialog.setWindowModality(Qt.ApplicationModal)

        dialog.raise_()
        dialog.activateWindow()
        if dialog.exec() == QFileDialog.Accepted:
            files = dialog.selectedFiles()
            for path in files:
                self._add_file_to_list_widget(file_list, path)

    def delete_selected(self, file_list):
        """Remove selected files"""
        for item in file_list.selectedItems():
            file_list.takeItem(file_list.row(item))

    def _add_file_to_list_widget(self, file_list, path):
        """Add file if its not already present."""
        if not path:
            return
        for index in range(file_list.count()):
            existing = file_list.item(index).data(Qt.UserRole)
            if existing == path:
                return

        display_name = os.path.basename(path) or path
        item = QListWidgetItem(display_name)
        item.setToolTip(path)
        item.setData(Qt.UserRole, path)
        file_list.addItem(item)

    def get_files_from_list_widget(self, file_list):
        """Collect all file paths from list widget."""
        files = []
        for index in range(file_list.count()):
            item = file_list.item(index)
            path = item.data(Qt.UserRole) or item.text()
            if path:
                files.append(path)
        return files

    def create_relation_selection(self, layout, available_items, title, selected_ids=None):
        """Create relation selection for Characters, Events, Places"""
        relation_widget = QListWidget()
        relation_widget.setSelectionMode(QListWidget.MultiSelection)
        relation_widget.setMaximumHeight(100)
        selected_ids = set(selected_ids or [])

        for item in available_items:
            list_item = QListWidgetItem(f"{item.name} ({item.id})")
            list_item.setData(Qt.UserRole, item.id)
            relation_widget.addItem(list_item)
            if item.id in selected_ids:
                list_item.setSelected(True)

        layout.addRow(f"Select {title}:", relation_widget)
        return relation_widget

    def create_single_place_selection(self, layout, available_places, selected_place_id=None):
        """Create place selection section using QComboBox"""
        place_combo = QComboBox()
        place_combo.addItem("No place selected", "")  # Default empty option

        selected_index = 0  
        for i, place in enumerate(available_places):
            place_combo.addItem(f"{place.name} ({place.id})", place.id)
            if selected_place_id and place.id == selected_place_id:
                selected_index = i + 1  # +1 because of the "No place selected" option

        place_combo.setCurrentIndex(selected_index)
        layout.addRow("Place:", place_combo)
        return place_combo

    def create_readonly_relation_display(self, layout, title, all_items, associated_ids):
        """Create display showing associated items"""
        if not all_items:
            display_widget = QLineEdit(f"No {title.lower()} available")
            display_widget.setReadOnly(True)
            layout.addRow(f"{title}:", display_widget)
            return display_widget

        associated_items = []
        associated_ids_set = set(associated_ids or [])
        for item in all_items:
            if item.id in associated_ids_set:
                associated_items.append(item)

        if associated_items:
            items_text = ", ".join([f"{item.name} ({item.id})" for item in associated_items])
        else:
            items_text = f"No {title.lower()} associated with this place"

        display_widget = QTextEdit()
        display_widget.setPlainText(items_text)
        display_widget.setReadOnly(True)
        display_widget.setMaximumHeight(60)
        display_widget.setMinimumHeight(40)
        display_widget.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        layout.addRow(f"{title}:", display_widget)
        return display_widget

    # Validation helper
    @staticmethod
    def validate_date_input(date_string, field_name= "Date"):
        """Validate date input with error handling"""
        if not date_string:
            return True, ""  

        date_string = date_string.strip()
        if not date_string:
            return True, ""
        # Check for Day format
        day_pattern = r'^Day\s+(\d+)$'
        day_match = re.match(day_pattern, date_string, re.IGNORECASE)
        if day_match:
            day_num = int(day_match.group(1))
            if day_num < 1:
                return False, f"{field_name} must be Day 1 or higher."
            if day_num > 99999:
                return False, f"{field_name} day number is too large (max 99999)."
            return True, ""
        # Check for date formats
        date_patterns = [
            r'^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})$',  # YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD
            r'^(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})$',  # DD-MM-YYYY, DD/MM/YYYY, DD.MM.YYYY
            r'^(\d{4})$',                              # Just year
        ]
        for pattern in date_patterns:
            match = re.match(pattern, date_string)
            if match:
                groups = match.groups()
                # year format
                if len(groups) == 1:
                    year = int(groups[0])
                    if year < 1 or year > 9999:
                        return False, f"{field_name} year must be between 1 and 9999."
                    return True, ""
                # Full format
                if pattern.startswith(r'^(\d{4})'):  # YYYY-MM-DD format
                    year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                else:  # DD-MM-YYYY format
                    day, month, year = int(groups[0]), int(groups[1]), int(groups[2])

                if year < 1 or year > 9999:
                    return False, f"{field_name} year must be between 1 and 9999."
                if month < 1 or month > 12:
                    return False, f"{field_name} month must be between 1 and 12."
                if day < 1 or day > 31:
                    return False, f"{field_name} day must be between 1 and 31."
                #month validation
                days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                if day > days_in_month[month - 1]:
                    return False, f"{field_name} day {day} is invalid for month {month}."

                return True, ""
        return False, f"{field_name} must be in format YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD, DD-MM-YYYY, DD/MM/YYYY, DD.MM.YYYY, just YYYY, or 'Day X'."

    @staticmethod
    def validate_file_path(filepath, for_reading= False):
    
        if not filepath or not isinstance(filepath, str):
            QMessageBox.warning(None, "Invalid File Path", "No file path provided.")
            return False

        filepath = filepath.strip()
        if not filepath:
            QMessageBox.warning(None, "Invalid File Path", "File path cannot be empty.")
            return False

        if len(filepath) > 255:
            QMessageBox.warning(None, "Invalid File Path", "File path is too long (max 255 characters).")
            return False
        # Check for invalid chars
        filename = os.path.basename(filepath)
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        if any(char in filename for char in invalid_chars):
            QMessageBox.warning(None, "Invalid File Name", f"File name cannot contain these characters: {', '.join(invalid_chars)}")
            return False
        try:
            if for_reading:
                if not os.path.exists(filepath):
                    QMessageBox.warning(None, "File Not Found", f"The file does not exist:\n{filepath}")
                    return False
                if not os.path.isfile(filepath):
                    QMessageBox.warning(None, "Invalid File", f"The path is not a file:\n{filepath}")
                    return False
                if not os.access(filepath, os.R_OK):
                    QMessageBox.warning(None, "Access Denied", f"Cannot read the file:\n{filepath}")
                    return False
            else: 
                directory = os.path.dirname(filepath)
                if directory and not os.path.exists(directory):
                    QMessageBox.warning(None, "Directory Not Found", f"The directory does not exist:\n{directory}")
                    return False
                if directory and not os.access(directory, os.W_OK):
                    QMessageBox.warning(None, "Access Denied", f"Cannot write to directory:\n{directory}")
                    return False

        except Exception as e:
            QMessageBox.warning(None, "File Path Error", f"Error validating file path:\n{str(e)}")
            return False

        return True

    @staticmethod
    def validate_name_input(name, entity_type= "Name"):
        """Validate names for Characters, Events, Places"""
        if not name or not isinstance(name, str):
            return False, f"{entity_type} cannot be empty."
        name = name.strip()
        if not name:
            return False, f"{entity_type} cannot be empty or contain only spaces."
        if len(name) > 100:
            return False, f"{entity_type} cannot be longer than 100 characters."
        if name.isdigit():
            return False, f"{entity_type} cannot be just numbers. Please provide a descriptive name."

        if not re.search(r'[a-zA-ZåäöÅÄÖ]', name):  #Swedish chars
            return False, f"{entity_type} must contain at least one letter."

        digit_count = sum(1 for char in name if char.isdigit())
        if len(name) > 0 and (digit_count / len(name)) > 0.5:
            return False, f"{entity_type} contains too many numbers. Please provide a more descriptive name."
        return True, ""
