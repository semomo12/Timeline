class NavigationController:
    """Handles view switching, zooming, and navigation"""

    def __init__(self, main):
        self.main = main
   
    def show_timeline(self):
        if hasattr(self.main, 'stackMain'):
            self.main.stackMain.setCurrentIndex(0)

    def show_table(self):
        if hasattr(self.main, 'stackMain'):
            self.main.stackMain.setCurrentIndex(1)

    def show_places(self):
        self.show_table()
        if hasattr(self.main, 'stackTables'):
            self.main.stackTables.setCurrentIndex(0)

    def show_chars(self):
        self.show_table()
        if hasattr(self.main, 'stackTables'):
            self.main.stackTables.setCurrentIndex(1)

    def show_events(self):
        self.show_table()
        if hasattr(self.main, 'stackTables'):
            self.main.stackTables.setCurrentIndex(2)

    def zoom_in(self):
        if hasattr(self.main, 'timeline_controller'):
            self.main.timeline_controller.zoom_in()

    def zoom_out(self):
        if hasattr(self.main, 'timeline_controller'):
            self.main.timeline_controller.zoom_out()

    def zoom_in_view(self):
        """Zoom in directly on the view"""
        view = getattr(self.main, "viewTimeline", None)
        if view:
            view.scale(1.2, 1.2)

    def zoom_out_view(self):
        """Zoom out directly on the view"""
        view = getattr(self.main, "viewTimeline", None)
        if view:
            view.scale(0.8, 0.8)

    def set_mode(self, mode):
        """Set display mode"""
        if mode in ['calendar', 'day_sequence']:
            self.main.timeline_mode = mode
            if hasattr(self.main, 'timeline_controller'):
                self.main.timeline_controller.update_timeline()

    def switch_mode(self):
        """switch between span and point display"""
        current = getattr(self.main, 'timeline_display_mode', 'span')
        new = 'point' if current == 'span' else 'span'
        self.main.timeline_display_mode = new

        if hasattr(self.main, 'timeline_controller'):
            self.main.timeline_controller.update_timeline()
 
    def filter_chars(self, char_ids):
        """Show events for specific characters"""
        timeline = getattr(self.main, 'timeline_controller', None)
        if timeline:
            timeline._filtered_characters = char_ids
            timeline.update_timeline()

    def refresh_all(self):
        """Update all views"""
        if hasattr(self.main, 'table_controller'):
            self.main.table_controller.update_tables()
        if hasattr(self.main, 'timeline_controller'):
            self.main.timeline_controller.update_timeline() 