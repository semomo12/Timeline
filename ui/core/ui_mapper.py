def map_ui_from_generated(main, ui):
    """Map UI elements from Ui_MainWindow"""
    # Main widgets
    main.btnTable = ui.btnTable
    main.btnTimeline = ui.btnTimeline
    main.stackMain = ui.stackMain
    split_timeline = getattr(ui, 'splitTimeline', None)
    main.splitTimeline = split_timeline
    list_places_widget = getattr(ui, 'listPlaces', None)
    main.viewTimeline = ui.viewTimeline

    if split_timeline and list_places_widget:
        index = split_timeline.indexOf(list_places_widget)
        if index != -1:
            widget = split_timeline.widget(index)
            widget.hide()
            widget.setParent(None)
        list_places_widget.deleteLater()
    main.listPlaces = None

    main.btnZoomIn = ui.btnZoomIn
    main.btnZoomOut = ui.btnZoomOut
    #Display mode
    if hasattr(ui, 'btnDisplayMode'):
        main.btnDisplayMode = ui.btnDisplayMode
    main.btnTablePlaces = ui.btnTablePlaces
    main.btnTableCharacters = ui.btnTableCharacters
    main.btnTableEvents = ui.btnTableEvents
    main.stackTables = ui.stackTables
    main.tablePlacesData = ui.tablePlacesData
    main.tableCharactersData = ui.tableCharactersData
    main.tableEventsData = ui.tableEventsData

    #Actions
    main.actionNewProject = ui.actionNewProject
    main.actionOpenProject = ui.actionOpenProject
    main.actionSaveProject = ui.actionSaveProject
    main.actionSaveChanges = ui.actionSaveChanges
    main.actionQuit = ui.actionQuit
    main.actionPlace = ui.actionPlace
    main.actionCharacterAdd = ui.actionCharacterAdd
    main.actionEvent = ui.actionEvent
    main.actionPlace_2 = ui.actionPlace_2
    main.actionCharacter = ui.actionCharacter
    main.actionEvent_2 = ui.actionEvent_2
    main.actionEditEvent = ui.actionEditEvent
    main.actionEditPlace = ui.actionEditPlace
    main.actionEditCharacter = ui.actionEditCharacter
    main.actionEditProjectName = ui.actionEditProjectName
    main.actionPlaces = ui.actionPlaces
    main.actionCharacters = ui.actionCharacters
    main.actionEvents = ui.actionEvents
    main.actionFilterCharacters = ui.actionFilterCharacters
    main.actionHelpGuide = ui.actionHelpGuide
    main.actionTimeline = ui.actionTimeline

    main._configure_edit_menu()
