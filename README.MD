# Timeline

An timeline application developed by Python and PySide6(QT).

## Overview

Timeline helps you create, visualize, and manage timelines with characters, events, and places. 



- **Two Timeline Modes**
  - 📅 **Calendar Dates**: Use real dates (YYYY-MM-DD)
  - 🔢 **Day Sequence**: Use relative days (Day 1, Day 2, etc.)

- **Entities**
  - 👤 **Characters**: People with age, description, colors, and images
  - 📍 **Events**: Occurrences with start/end dates, participants, and locations
  - 🏠 **Places**: Locations where events take place



## Interactive & UI Features 

  - Entity management: characters, events, locations
  - UI features: dark/light mode, table views, filtering, image upload, JSON export/import
  - Drag-and-drop characters between events
  - Click to view/edit details
  - Right-click for context menus
  - Zoom in/out on timeline
  - Keyboard shortcuts (Ctrl+S for saving project/changes)

- **Validation**
- No overlapping events for characters
- Duplicate checking
- Date validation



## Installation

### Requirements
- Python3 
- PySide6
- Pytest

### Steps
Clone or download the project:

git clone <https://github.com/semomo12/Timeline.git>

### Create and activate a virtual environment#
```bash
python3 -m venv venv
source venv/bin/activate
```
### Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## To generate a Python file from .ui
```bash
pyside6-uic ui/core/main_window.ui -o ui/core/main_window_ui.py
```

### Start the Application
app/main.py
```bash
python app/main.py
```
or use start.sh:
```bash
./start.sh
```
### Keyboard Shortcuts

- `Ctrl+S`: Save project/changes


### Quick Start
1. **Create a new project**: File → New Project
2. **Add a place**: Add Place
3. **Add a character**: Add Character
4. **Create an event**: Add Event
   - Choose date/day sequence
   - Select place
   - Select participating characters
5. **Visualize**: Timeline updates automatically

### Drag-and-Drop
1. Click and hold on a character in an event
2. Drag to another event
3. Release to move the character
The application automatically validates that the move is allowed (no overlapping events).



## Project Structure

```

├── README.MD                  # Project description and instructions
├── Tests                      # Unit tests
│   └── test_basic_entities.py   # Tests for basic entities
├── app                        # Application entry point
│   └── main.py                  # Main file to start the program
├── core                       # Core logic and data models
│   ├── data                     # Data models (character, event, place, project)
│   │   ├── base_model.py          # Base model for other data models
│   │   ├── character.py           # Model for characters
│   │   ├── data_manager.py        # Data and storage management
│   │   ├── event.py               # Model for events
│   │   ├── place.py               # Model for places
│   │   ├── project.py             # Model for projects
│   │   └── timeline_data.py       # Model for timeline data
│   ├── logic                    # Controllers and logic
│   │   ├── main_controller.py      # Main controller for the application
│   │   ├── objects                # Object controllers (character, event, place)
│   │   ├── project_controller.py   # Controller for projects
│   │   └── ui                     # UI-related logic
│   └── utils                    # Helper functions and validation
│       ├── timeline_helpers.py     # Timeline helper functions
│       └── validation_manager.py   # Validation logic
├── requirements.txt            # Python dependencies
├── start.sh                    # Startup script for the application
└── ui                          # UI components and rendering
  ├── click_handler.py          # Handles UI clicks
  ├── core
  │   ├── main_window_ui.py       # UI class for main window
  │   └── ui_mapper.py            # Mapper between UI and data
  ├── drag_drop.py               # Drag-and-drop functionality
  ├── graphics
  │   ├── color.py                  # Color management
  │   ├── drawing.py                # Drawing logic
  │   ├── layout.py                 # Graphics layout
  │   ├── participants.py           # Handles participants in graphics
  │   └── render.py                 # Graphics rendering
  ├── info_dialogs.py             # Information dialogs
  ├── menu_factory.py             # Menu management
  ├── navigation.py               # UI navigation
  └── scene.py                    # Scene management in UI

```


## Project saves as JSON files
```json
{
  "name": "My Project",
  "characters": [...],
  "events": [...],
  "places": [...],
  "metadata": {
    "timeline_mode": "calendar",
    "dark_mode_enabled": false
  }
}
```


## Known Limitations

- An event can only be associated with one place
- Characters cannot be in overlapping events
- Descriptions and notes limited to 200 characters


## Testing
- TestCharacterOperations (4 tests): Create, edit, serialize characters
- TestEventOperations (3 tests): Create, edit, serialize events
- TestPlaceOperations (2 tests): Create, edit, serialize places
- TestProjectIntegration (3 tests): Project with all entities, relationships


### Run All Tests:
```bash
pip install pytest
python3 -m pytest Tests/test_basic_entities.py -v
```

### Test certain parts:
```bash
pytest Tests/test_basic_entities.py -k TestCharacterOperations -v
pytest Tests/test_basic_entities.py -k test_create_characters -v
pytest Tests/test_basic_entities.py -k TestEventOperations -v
pytest Tests/test_basic_entities.py::TestCharacterOperations::test_create_characters -v

```

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-28

---

## Author

[Seyed Mostafa Mohseni]
PA1414