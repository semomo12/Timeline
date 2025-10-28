from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QDialog, QVBoxLayout, QScrollArea, QWidget,QCheckBox, QPushButton, QLabel

class MenuController:
    """Manages menu creation, actions, and signal connections"""

    def __init__(self, main_controller):
        self.main_controller = main_controller

    def config_edit_menu(self, edit_menu=None):
        """configure Edit menu if it has right actions."""
        menubar = self.main_controller.menuBar()
        if edit_menu is None:
            for action in menubar.actions():
                menu = action.menu()
                if menu and action.text().replace('&', '') == 'Edit':
                    edit_menu = menu
                    break
            if edit_menu is None:
                edit_menu = menubar.addMenu("Edit")

        for action in list(edit_menu.actions()):
            edit_menu.removeAction(action)
   
        if not hasattr(self.main_controller, 'actionEditPlace') or self.main_controller.actionEditPlace is None:
            self.main_controller.actionEditPlace = QAction("Place", self.main_controller)
        if not hasattr(self.main_controller, 'actionEditCharacter') or self.main_controller.actionEditCharacter is None:
            self.main_controller.actionEditCharacter = QAction("Character", self.main_controller)
        if not hasattr(self.main_controller, 'actionEditEvent') or self.main_controller.actionEditEvent is None:
            self.main_controller.actionEditEvent = QAction("Event", self.main_controller)
        if not hasattr(self.main_controller, 'actionEditProject') or self.main_controller.actionEditProject is None:
            self.main_controller.actionEditProject = QAction("Project", self.main_controller)

        #Add actions
        edit_menu.addAction(self.main_controller.actionEditProject)
        edit_menu.addAction(self.main_controller.actionEditEvent)
        edit_menu.addAction(self.main_controller.actionEditPlace)
        edit_menu.addAction(self.main_controller.actionEditCharacter)

        self.main_controller.menuEdit = edit_menu
        return edit_menu

    def connect_signals(self):
        """Connect UI to their handlers"""
        # File menu
        if hasattr(self.main_controller, 'actionNewProject') and self.main_controller.actionNewProject:
            self.main_controller.actionNewProject.triggered.connect(self.main_controller.project_controller.new)
        if hasattr(self.main_controller, 'actionOpenProject') and self.main_controller.actionOpenProject:
            self.main_controller.actionOpenProject.triggered.connect(self.main_controller.project_controller.open)
        if hasattr(self.main_controller, 'actionSaveProject') and self.main_controller.actionSaveProject:
            self.main_controller.actionSaveProject.triggered.connect(self.main_controller.project_controller.save)
        if hasattr(self.main_controller, 'actionSaveChanges') and self.main_controller.actionSaveChanges:
            self.main_controller.actionSaveChanges.triggered.connect(self.main_controller.project_controller.save)
        if hasattr(self.main_controller, 'actionExport') and self.main_controller.actionExport:
            self.main_controller.actionExport.triggered.connect(self.main_controller.project_controller.save_as)
        if hasattr(self.main_controller, 'actionQuit') and self.main_controller.actionQuit:
            self.main_controller.actionQuit.triggered.connect(self.main_controller.close)

        #Add menu
        if hasattr(self.main_controller, 'actionPlace') and self.main_controller.actionPlace:
            self.main_controller.actionPlace.triggered.connect(self.main_controller.place_controller.add)
        if hasattr(self.main_controller, 'actionCharacterAdd') and self.main_controller.actionCharacterAdd:
            self.main_controller.actionCharacterAdd.triggered.connect(self.main_controller.character_controller.add)
        if hasattr(self.main_controller, 'actionEvent') and self.main_controller.actionEvent:
            self.main_controller.actionEvent.triggered.connect(self.main_controller.event_controller.add)

        #Remove menu
        if hasattr(self.main_controller, 'actionPlace_2') and self.main_controller.actionPlace_2:
            self.main_controller.actionPlace_2.triggered.connect(self.main_controller.place_controller.remove)
        if hasattr(self.main_controller, 'actionCharacter') and self.main_controller.actionCharacter:
            self.main_controller.actionCharacter.triggered.connect(self.main_controller.character_controller.remove)
        if hasattr(self.main_controller, 'actionEvent_2') and self.main_controller.actionEvent_2:
            self.main_controller.actionEvent_2.triggered.connect(self.main_controller.event_controller.remove)

        #DisplayMode switch button
        if hasattr(self.main_controller, 'btnDisplayMode') and self.main_controller.btnDisplayMode:
            self.main_controller.btnDisplayMode.clicked.connect(self.main_controller.theme_controller.toggle_display_mode)

        #View menu
        if hasattr(self.main_controller, 'actionPlaces') and self.main_controller.actionPlaces:
            self.main_controller.actionPlaces.triggered.connect(self.main_controller.navigation_controller.show_places)
        if hasattr(self.main_controller, 'actionCharacters') and self.main_controller.actionCharacters:
            self.main_controller.actionCharacters.triggered.connect(self.main_controller.navigation_controller.show_chars)
        if hasattr(self.main_controller, 'actionEvents') and self.main_controller.actionEvents:
            self.main_controller.actionEvents.triggered.connect(self.main_controller.navigation_controller.show_events)

        #Edit menu
        if hasattr(self.main_controller, 'actionEditPlace') and self.main_controller.actionEditPlace:
            self.main_controller.actionEditPlace.triggered.connect(self.main_controller.place_controller.edit)
        if hasattr(self.main_controller, 'actionEditCharacter') and self.main_controller.actionEditCharacter:
            self.main_controller.actionEditCharacter.triggered.connect(self.main_controller.character_controller.edit)
        if hasattr(self.main_controller, 'actionEditProjectName') and self.main_controller.actionEditProjectName:
            self.main_controller.actionEditProjectName.triggered.connect(self.main_controller.project_controller.edit_project_name)
        if hasattr(self.main_controller, 'actionEditEvent') and self.main_controller.actionEditEvent:
            self.main_controller.actionEditEvent.triggered.connect(self.main_controller.event_controller.edit)
        if hasattr(self.main_controller, 'actionEditProject') and self.main_controller.actionEditProject:
            self.main_controller.actionEditProject.triggered.connect(self.main_controller.project_controller.edit_project)

        #Filter menu
        if hasattr(self.main_controller, 'actionFilterCharacters') and self.main_controller.actionFilterCharacters:
            self.main_controller.actionFilterCharacters.triggered.connect(lambda: self.main_controller.apply_filter('characters'))

        #Help menu
        if hasattr(self.main_controller, 'actionHelpGuide') and self.main_controller.actionHelpGuide:
            self.main_controller.actionHelpGuide.triggered.connect(self.main_controller.show_help)

        #About menu
        if hasattr(self.main_controller, 'actionTimeline') and self.main_controller.actionTimeline:
            self.main_controller.actionTimeline.triggered.connect(self.main_controller.about)

        #Table/Timeline buttons
        if hasattr(self.main_controller, 'btnTable') and self.main_controller.btnTable:
            self.main_controller.btnTable.clicked.connect(self.main_controller.navigation_controller.show_table)
        if hasattr(self.main_controller, 'btnTimeline') and self.main_controller.btnTimeline:
            self.main_controller.btnTimeline.clicked.connect(self.main_controller.navigation_controller.show_timeline)

        #Tables buttons
        if hasattr(self.main_controller, 'btnTablePlaces') and self.main_controller.btnTablePlaces:
            self.main_controller.btnTablePlaces.clicked.connect(self.main_controller.navigation_controller.show_places)
        if hasattr(self.main_controller, 'btnTableCharacters') and self.main_controller.btnTableCharacters:
            self.main_controller.btnTableCharacters.clicked.connect(self.main_controller.navigation_controller.show_chars)
        if hasattr(self.main_controller, 'btnTableEvents') and self.main_controller.btnTableEvents:
            self.main_controller.btnTableEvents.clicked.connect(self.main_controller.navigation_controller.show_events)

        #Zoom buttons
        if hasattr(self.main_controller, 'btnZoomIn') and self.main_controller.btnZoomIn:
            self.main_controller.btnZoomIn.clicked.connect(self.main_controller.navigation_controller.zoom_in)
        if hasattr(self.main_controller, 'btnZoomOut') and self.main_controller.btnZoomOut:
            self.main_controller.btnZoomOut.clicked.connect(self.main_controller.navigation_controller.zoom_out)

    def show_help(self):
        """Show help dialog"""
        QMessageBox.information(
            self.main_controller,
            'Help Guide',
            'Timeline Application Help:\n\n'
            '• File Menu: Create, open, save project and save changes by ctrl+s\n\n'
            '• Add Menu: Create new characters, events, places\n\n'
            '• Remove Menu: Delete selected characters, events or places\n\n'
            '• Edit Menu: Modify existing items\n\n'
            '• View Menu: To see the lists of characters, events or places\n\n'
            '• Filter Menu: Focus on specific character/characters in the timeline\n\n'
            '• Use the ⚏ , ▦  to switch views\n\n'
            '• Use + , -  to navigate timeline\n\n'
            '• Left Mouse Click: Default behavior (selects/moves items).\n\n'
            '• Right Mouse Click: Opens dialogs for editing/viewing details of items.\n\n'
            '• Drag and Drop: Move characters along the timeline.\n\n'
            '• You can move character to the top of the list in an event block by dragging them.\n\n'
            '• You will see the project name and  * ( when you have unsaved changes) on the top of the window\n\n'
            '• Note: You should use the *Edit options* to make modifications. '
            'Editing elements directly in the table columns should be avoided.\n\n'
        )

    def about(self):
        """Show about dialog"""
        QMessageBox.about(
            self.main_controller,
            'About Timeline',
            'Timeline Application\nVersion 1.0.0\n\n'
            'A tool for managing characters, events, and places in timelines.\n\n'

        )

    def apply_filter(self, filter_type):
        """Apply filter based on type"""
        if filter_type == 'characters':
            self.display_char_filter_dialog()
        else:
            if not hasattr(self.main_controller, 'stackMain') or not self.main_controller.stackMain:
                return
            self.main_controller.stackMain.setCurrentIndex(1)
            index_value = None
            if filter_type == 'events':
                index_value = 2
            elif filter_type == 'places':
                index_value = 0
            elif filter_type == 'characters':
                index_value = 1
            if index_value is not None and hasattr(self.main_controller, 'stackTables') and self.main_controller.stackTables:
                self.main_controller.stackTables.setCurrentIndex(index_value)

    def display_char_filter_dialog(self):
        """Show dialog to select characters for filtering."""
        if not hasattr(self.main_controller, 'project') or not self.main_controller.project or not self.main_controller.project.characters:
            QMessageBox.information(self.main_controller, 'No Characters', 'No characters available to filter.')
            return

        dialog = QDialog(self.main_controller)
        dialog.setWindowTitle('Character Focus Mode')
        dialog.setModal(True)
        dialog.resize(320, 450)

        layout = QVBoxLayout(dialog)
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        checkboxes = {}
        current_filtered = getattr(self.main_controller, '_filtered_characters', set())

        characters_in_events = set()
        for event in self.main_controller.project.events:
            if hasattr(event, 'participants'):
                for participant_id in event.participants:
                    characters_in_events.add(participant_id)

        avlbe_chars = []
        for character in self.main_controller.project.characters:
            if character.id in characters_in_events:
                avlbe_chars.append(character)

        if not avlbe_chars:
            no_chars_label = QLabel("No characters are participating in any events yet.")
            scroll_layout.addWidget(no_chars_label)
        else:
            for character in avlbe_chars:
                checkbox = QCheckBox(character.name or f"Character {character.id}")
                checkbox.setChecked(character.id in current_filtered)
                checkboxes[character.id] = checkbox
                scroll_layout.addWidget(checkbox)

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        button_layout = QVBoxLayout()
        apply_btn = QPushButton('Enable Focus')
        reset_btn = QPushButton('Reset')
        button_layout.addWidget(apply_btn)
        button_layout.addWidget(reset_btn)
        layout.addLayout(button_layout)

        def apply_filter():
            selected_ids = set()
            for char_id, checkbox in checkboxes.items():
                if checkbox.isChecked():
                    selected_ids.add(char_id)
            self.enable_char_filter(selected_ids)
            dialog.accept()

        def clear_filter():
            self.enable_char_filter(set())
            dialog.accept()

        apply_btn.clicked.connect(apply_filter)
        reset_btn.clicked.connect(clear_filter)

        dialog.exec()

    def enable_char_filter(self, character_ids):
        """Apply filter and update timeline highlighting"""

        self.main_controller._filtered_characters = character_ids
        if hasattr(self.main_controller, 'stackMain') and self.main_controller.stackMain:
            self.main_controller.stackMain.setCurrentIndex(0)
        if hasattr(self.main_controller, 'timeline_controller') and self.main_controller.timeline_controller:
            self.main_controller.timeline_controller.navigation_manager.filter_chars(character_ids)

        if character_ids:
            character_names = []
            for char in self.main_controller.project.characters:
                if char.id in character_ids:
                    label = char.name if char.name else f"Character {char.id}"
                    character_names.append(label)
            names_text = ", ".join(character_names)
            QMessageBox.information(self.main_controller, 'Focus Enabled', f"Focusing on: {names_text}")
        else:
            QMessageBox.information(self.main_controller, 'Focus Reset', 'Focus mode disabled.')
