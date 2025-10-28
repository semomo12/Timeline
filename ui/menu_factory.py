from PySide6.QtGui import QAction

def create_basic_menus(main):
    """Create menus"""
    menubar = main.menuBar()
    
    for action in list(menubar.actions()):
        menubar.removeAction(action)
    #File
    file_menu = menubar.addMenu("File")
    main.actionNewProject = QAction("New", main)
    main.actionOpenProject = QAction("Open", main)
    main.actionSaveProject = QAction("Save", main)
    main.actionSaveChanges = QAction("Save Changes", main)
    main.actionSaveChanges.setShortcut("Ctrl+S")
    main.actionQuit = QAction("Exit", main)

    file_menu.addAction(main.actionNewProject)
    file_menu.addAction(main.actionOpenProject)
    file_menu.addAction(main.actionSaveProject)
    file_menu.addSeparator()
    file_menu.addAction(main.actionSaveChanges)
    file_menu.addSeparator()
    file_menu.addAction(main.actionQuit)
    #Add
    add_menu = menubar.addMenu("Add")
    main.actionEvent = QAction("Event", main)
    main.actionPlace = QAction("Place", main)
    main.actionCharacterAdd = QAction("Character", main)
    add_menu.addAction(main.actionEvent)
    add_menu.addAction(main.actionPlace)
    add_menu.addAction(main.actionCharacterAdd)
    #Remove
    remove_menu = menubar.addMenu("Remove")
    main.actionEvent_2 = QAction("Event", main)
    main.actionPlace_2 = QAction("Place", main)
    main.actionCharacter = QAction("Character", main)
    remove_menu.addAction(main.actionEvent_2)
    remove_menu.addAction(main.actionPlace_2)
    remove_menu.addAction(main.actionCharacter)
    #Edit
    edit_menu = menubar.addMenu("Edit")
    main.actionEditEvent = QAction("Event", main)
    main.actionEditPlace = QAction("Place", main)
    main.actionEditCharacter = QAction("Character", main)
    edit_menu.addAction(main.actionEditEvent)
    edit_menu.addAction(main.actionEditPlace)
    edit_menu.addAction(main.actionEditCharacter)
    edit_menu.addSeparator()
    main.actionEditProjectName = QAction("Project Name", main)
    edit_menu.addAction(main.actionEditProjectName)
    #View
    view_menu = menubar.addMenu("View")
    main.actionEvents = QAction("Events", main)
    main.actionPlaces = QAction("Places", main)
    main.actionCharacters = QAction("Characters", main)
    view_menu.addAction(main.actionEvents)
    view_menu.addAction(main.actionPlaces)
    view_menu.addAction(main.actionCharacters)
    view_menu.addSeparator()
    #Filter
    filter_menu = menubar.addMenu("Filter")
    main.actionFilterCharacters = QAction("Characters", main)
    filter_menu.addAction(main.actionFilterCharacters)
    #Help
    help_menu = menubar.addMenu("Help")
    main.actionTimeline = QAction("About", main)
    main.actionHelpGuide = QAction("How to Use Timeline", main)
    help_menu.addAction(main.actionTimeline)
    help_menu.addAction(main.actionHelpGuide)