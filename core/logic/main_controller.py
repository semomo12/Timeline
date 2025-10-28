import os
import sys
import uuid
from PySide6.QtWidgets import QMainWindow
from core.data.project import Project
from core.logic.ui.theme_controller import ThemeController
from core.logic.project_controller import ProjectController
from core.logic.ui.ui_controller import UIController
from core.utils.timeline_helpers import HelperController
from core.logic.ui.menu_controller import MenuController
from core.logic.objects.character_controller import CharacterController
from core.logic.objects.event_controller import EventController
from core.logic.objects.place_controller import PlaceController
from core.logic.ui.timeline_controller import TimelineController
from core.logic.ui.table_controller import TableController
from ui.navigation import NavigationController
from ui.core.ui_mapper import map_ui_from_generated
from ui.menu_factory import create_basic_menus
from ui.graphics.color import build_dark_palette
from core.utils.validation_manager import TimelineValidationManager
from ui.core.main_window_ui import Ui_MainWindow as UiClass

UI_LOADED = True
#ui directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ui'))

class MainController(QMainWindow):
    """Main controller coordinates all other controllers"""

    def __init__(self):
        super().__init__()
        print("start")

        self.initialize_defaults()

        self.project = Project()
        self._initialize_project_state(new_project=True)

        self.ui_controller = UIController(self)
        self.load_ui()

        self.create_controllers()
        self.finish_startup()
        print("done")

    def initialize_defaults(self):
        """Prepare the default state for the controller."""
        # Project state
        self.project_dirty = False
        self.dark_mode_enabled = False
        self.timeline_mode = "calendar"
        self.timeline_mode_locked = False
        self.timeline_display_mode = "span"
        self.timeline_display_mode_locked = False
        self.current_file = None

        # Menu state
        self.menuEdit = None

        # Timeline widgets
        self.stackMain = None
        self.viewTimeline = None
        self.stackTables = None
        self.tablePlacesData = None
        self.tableCharactersData = None
        self.tableEventsData = None

        # Basic UI buttons
        self.btnDisplayMode = None
        self.btnTimeline = None
        self.btnTable = None
        self.btnZoomIn = None
        self.btnZoomOut = None
        self.btnTablePlaces = None
        self.btnTableCharacters = None
        self.btnTableEvents = None

    def load_ui(self):
        """Load UI."""

        if UI_LOADED:
            try:    
                self.ui = UiClass()
                self.ui.setupUi(self)
                map_ui_from_generated(self, self.ui)
                print("UI loaded")
                self.copy_actions_from_ui()
            except ImportError as error:
                print(f"Failed to load UI: {error}")
                self.ui_controller.create_basic_ui()
                print("try 2, Using basic UI")
        else:
            self.ui_controller.create_basic_ui()
            print("Using basic UI")

    def copy_actions_from_ui(self):
        """Copy QAction objects from the generated UI"""
        self.actionNewProject = self.ui.actionNewProject
        self.actionOpenProject = self.ui.actionOpenProject
        self.actionSaveProject = self.ui.actionSaveProject
        self.actionSaveChanges = self.ui.actionSaveChanges
        self.actionQuit = self.ui.actionQuit
        self.actionEditEvent = self.ui.actionEditEvent
        self.actionEditPlace = self.ui.actionEditPlace
        self.actionEditCharacter = self.ui.actionEditCharacter
        self.actionEditProjectName = self.ui.actionEditProjectName
        self.actionFind_Ctrl_F = self.ui.actionFind_Ctrl_F
        self.actionPlace = self.ui.actionPlace
        self.actionCharacterAdd = self.ui.actionCharacterAdd
        self.actionEvent = self.ui.actionEvent
        self.actionPlace_2 = self.ui.actionPlace_2
        self.actionCharacter = self.ui.actionCharacter
        self.actionEvent_2 = self.ui.actionEvent_2
        self.actionToday_2 = self.ui.actionToday_2

    def create_controllers(self):
        """Instantiate controllers."""
        self.theme_controller = ThemeController(self)
        self.project_controller = ProjectController(self)

        self.helper_controller = HelperController(self)
        
        self.validation_manager = TimelineValidationManager(self)
        self.character_controller = CharacterController(self)
        self.event_controller = EventController(self)
        self.place_controller = PlaceController(self)

        self.timeline_controller = TimelineController(self)
        self.table_controller = TableController(self)
        self.table_controller.attach_table_signals()
        self.navigation_controller = NavigationController(self)

        self.menu_controller = MenuController(self)
        print(" Controllers created")

    def finish_startup(self):
        """Finalize menus, signals and initial UI refresh."""
        if UI_LOADED:
            create_basic_menus(self)

        print(" Connecting signals")
        self.menu_controller.connect_signals()
        print(" Signals connected")

        print(" Update UI")
        self._update_ui()
        print(" Update window title")
        self._update_window_title()
        if not UI_LOADED:
            self.setGeometry(100, 100, 1200, 800)
        
        
    def _initialize_project_state(self, new_project= True):
        """Initialize project state variables"""
        if new_project:
            self.timeline_mode = "calendar"
            self.timeline_mode_locked = False
            self.timeline_display_mode = "span"
            self.timeline_display_mode_locked = False
        else:
            metadata = getattr(self.project, 'metadata', {}) or {}
            self.timeline_mode = metadata.get('timeline_mode', "calendar")
            self.timeline_mode_locked = bool(metadata.get('timeline_mode_locked', False))
            self.timeline_display_mode = metadata.get('timeline_display_mode', "span")
            self.timeline_display_mode_locked = bool(metadata.get('timeline_display_mode_locked', False))
            self.dark_mode_enabled = bool(metadata.get('dark_mode_enabled', False))

            self._migrate_project_ids()
            self.update_character_event_links()

            if 'timeline_mode' not in metadata and self.project.events:
                inferred_mode = getattr(self.project.events[0], 'timeline_mode', None)
                if inferred_mode:
                    self.timeline_mode = inferred_mode
                    self.timeline_mode_locked = True
        self._maybe_unlock_timeline_modes()

        if hasattr(self, 'theme_controller') and self.theme_controller:
            self.theme_controller.sync_theme_state()

    def show(self):
        """Override show to ensure window comes to front"""
        super().show()
        self.raise_()
        self.activateWindow()

    def _update_ui(self):
        """call UIController"""
        if hasattr(self, 'ui_controller'):
            self.ui_controller.update_ui()

    def _update_window_title(self):
        """Updates the window title with the project name and save status"""
        title = "Timeline"
        if self.project and hasattr(self.project, 'name') and self.project.name:
            title = f"Timeline - {self.project.name}"
        if self.project_dirty:
            title += " *"
        self.setWindowTitle(title)

    def _sync_timeline_settings(self):
        """Persist timeline settings in project metadata."""
        self.project.metadata['timeline_mode'] = self.timeline_mode
        self.project.metadata['timeline_mode_locked'] = self.timeline_mode_locked
        self.project.metadata['timeline_display_mode'] = self.timeline_display_mode
        self.project.metadata['timeline_display_mode_locked'] = self.timeline_display_mode_locked
        self.project.metadata['dark_mode_enabled'] = self.dark_mode_enabled

    def _maybe_unlock_timeline_modes(self):
        """Unlock timeline settings when the project no longer has events."""
        events = getattr(self.project, 'events', None)
        if not events:
            self.timeline_mode_locked = False
            self.timeline_display_mode_locked = False

    def mark_project_dirty(self, dirty= True):
        """Sets the project's dirty state and updates the UI."""
        self.project_dirty = dirty
        self._update_window_title()

    def mark_dirty(self, dirty: bool = True):
        """Retains support for legacy calls to mark_dirty() by forwarding to mark_project_dirty()."""
        return self.mark_project_dirty(dirty)

    def _configure_edit_menu(self, edit_menu=None):
        if hasattr(self, 'menu_controller'):
            return self.menu_controller.configure_edit_menu(edit_menu)

    # Navigation 
    def show_list(self, list_type):
        """Show list in the table view"""
        if hasattr(self, 'navigation_controller'):
            if list_type == 'places':
                self.navigation_controller.show_places()
            elif list_type == 'characters':
                self.navigation_controller.show_characters()
            elif list_type == 'events':
                self.navigation_controller.show_events()

    def _switch_to_timeline(self):
        """Switch main view to timeline"""
        if hasattr(self, 'navigation_controller'):
            self.navigation_controller.show_timeline()

    def zoom_in(self):
        if hasattr(self, 'navigation_controller'):
            self.navigation_controller.zoom_in()

    def zoom_out(self):
        if hasattr(self, 'navigation_controller'):
            self.navigation_controller.zoom_out()

    # Helper controller
    def show_info_message(self, title, message):
        if hasattr(self, 'helper_controller'):
            self.helper_controller.show_info_message(title, message)

    def maybe_save_before_action(self, action_description= "performing this action"):
        """Check if user wants save before action"""
        if hasattr(self, 'helper_controller'):
            return self.helper_controller.maybe_save_before_action(action_description)
        return True

    def normalize_name(self, name):
        """Normalize name for comparison"""
        if hasattr(self, 'helper_controller'):
            return HelperController.normalize_name(name)
        return name.strip().lower()

    def is_name_taken(self, entity_type, name, exclude_id= None):
        """Check if name is already taken"""
        if hasattr(self, 'helper_controller'):
            return self.helper_controller.is_name_taken(entity_type, name, exclude_id)
        return False

    def _events_overlap(self, event1, event2):
        """Check if two events overlap"""
        if hasattr(self, 'helper_controller'):
            return self.helper_controller._events_overlap(event1, event2)
        return False

    def _update_character_places_from_events(self, character):
        """Update character places from events"""
        if hasattr(self, 'helper_controller'):
            self.helper_controller.update_char_places(character)

    def _next_day_index(self):
        """Calculate next day sequence index"""
        if hasattr(self, 'helper_controller'):
            return self.helper_controller.next_day_index()
        return 1

    def _parse_date(self, value):
        """Parse event date"""
        if hasattr(self, 'helper_controller'):
            return self.helper_controller.parse_date(value)
        return None

    def _validate_char_events(self, event_ids):
        """Validate character event selection"""
        if hasattr(self, 'validation_manager'):
            return self.validation_manager.validate_char_events(event_ids)
        return True

    def _validate_event_chars(self,
        event_name,
        start_date,
        end_date,
        timeline_mode,
        day_index,
        day_index_end,
        character_ids,
        event_id=None,
    ):
        """
        Asks the validation manager to verify that selected characters match event constraints.
        If no validation manager is available, assumes the selection is valid.
        """
        if hasattr(self, 'validation_manager'):
            return self.validation_manager.validate_event_chars(
                event_name, start_date, end_date, timeline_mode,
                day_index, day_index_end, character_ids, event_id)
        return True

    def _deduplicate_ids(self, id_list):
        if hasattr(self, 'helper_controller'):
            return HelperController.deduplicate_ids(id_list)
        return list(id_list) if id_list else []

    def _parse_day_index(self, value):
        if hasattr(self, 'helper_controller'):
            return self.helper_controller._parse_day_index(value)
        return None

    def _append_unique(self, container, value):
        """Append unique value"""
        if hasattr(self, 'helper_controller'):
            HelperController.append_unique(container, value)
        elif value and value not in container:
            container.insert(0, value)

   
    def apply_filter(self, filter_type):
        if hasattr(self, 'menu_controller'):
            self.menu_controller.apply_filter(filter_type)

    def show_help(self):
        if hasattr(self, 'menu_controller'):
            self.menu_controller.show_help()

    def about(self):
        if hasattr(self, 'menu_controller'):
            self.menu_controller.about()

    def _migrate_project_ids(self):
        """Generate IDs for project entities that don't have them"""
        #events
        events_migrated = 0
        for event in self.project.events:
            if not hasattr(event, 'id') or not event.id:
                event.id = str(uuid.uuid4())
                events_migrated += 1

        #characters
        characters_migrated = 0
        for character in self.project.characters:
            if not hasattr(character, 'id') or not character.id:
                character.id = str(uuid.uuid4())
                characters_migrated += 1

        #places
        places_migrated = 0
        for place in self.project.places:
            if not hasattr(place, 'id') or not place.id:
                place.id = str(uuid.uuid4())
                places_migrated += 1

        if events_migrated > 0 or characters_migrated > 0 or places_migrated > 0:
            print(f"Project migration: Generated {events_migrated} event IDs, {characters_migrated} character IDs, {places_migrated} place IDs")
            self.mark_dirty(True)

    def update_character_event_links(self):
        """check character.associated_events is synced with event.participants"""
        for character in self.project.characters:
            if not hasattr(character, 'associated_events'):
                character.associated_events = []
            else:
                character.associated_events.clear()

        for event in self.project.events:
            if hasattr(event, 'participants') and event.participants:
                for char_id in event.participants:
                    character = next((ch for ch in self.project.characters if ch.id == char_id), None)
                    if character:
                        if not hasattr(character, 'associated_events'):
                            character.associated_events = []
                        if event.id not in character.associated_events:
                            character.associated_events.append(event.id)

        print("Character-event associations synced.")
