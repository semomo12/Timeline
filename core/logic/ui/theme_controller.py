from PySide6.QtWidgets import QApplication
from ui.graphics.color import build_dark_palette

class ThemeController:
    """Manages theme and display mode"""

    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.light_palette = None
        self.dark_palette = None
        self.light_stylesheet = ""
        self.load_paletts()

    def load_paletts(self):
        """Store current light palette and stylesheet."""
        app = QApplication.instance()
        if not app:
            self.light_palette = None
            self.dark_palette = None
            self.light_stylesheet = ""
            return

        self.light_palette = app.palette()
        self.dark_palette = self.create_dark_palett(self.light_palette)
        self.light_stylesheet = app.styleSheet()

    def toggle_display_mode(self):
        """switch dark,light mode and refresh UI"""
        self.main_controller.dark_mode_enabled = not self.main_controller.dark_mode_enabled
        self.apply_theme()

    def sync_theme_state(self):
        """Apply theme that matches stored dark_mode_enabled flag."""
        self.apply_theme()

    def apply_theme(self):
        app = QApplication.instance()
        if not app:
            return

        dark_mode = bool(getattr(self.main_controller, "dark_mode_enabled", False))

        if dark_mode:
            if self.dark_palette:
                app.setPalette(self.dark_palette)
            tooltip_style = "\nQToolTip { color: #ffffff; background-color: #333333; border: 1px solid #bbbbbb; }"
            app.setStyleSheet(self.light_stylesheet + tooltip_style)
            self.set_mode_button("☾")
        else:
            if self.light_palette:
                app.setPalette(self.light_palette)
            app.setStyleSheet(self.light_stylesheet)
            self.set_mode_button("☼")

        self._refresh_timeline()

    def set_mode_button(self, text):
        button = getattr(self.main_controller, "btnDisplayMode", None)
        if button:
            button.setText(text)

    def _refresh_timeline(self):
        timeline = getattr(self.main_controller, "timeline_controller", None)
        if timeline:
            timeline.update_timeline()

    def create_dark_palett(self, base_palette=None):
        """make darkpalette using theme helper."""
        return build_dark_palette(base_palette)