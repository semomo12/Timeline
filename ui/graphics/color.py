from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette

class TimelineColorManager:
    """Manages colors for timeline elements"""
    EVENT_COLOR_PALETTE = [
        QColor("#FDE2E4"), QColor("#C9E4DE"), QColor("#F0EFEB"), QColor("#D0E6A5"),
        QColor("#FFEDB5"), QColor("#E6E6FA"), QColor("#FFE5D9"), QColor("#D7E9B9"),
        QColor("#F8F3D4"), QColor("#DCEEF2"), QColor("#FFEFD5"), QColor("#F3E8FF")
    ]
    
    def __init__(self, timeline_controller):
        self.timeline_controller = timeline_controller
        self._event_color_cache: Dict[str, QColor] = {}
        self._place_color_cache: Dict[str, str] = {}

    def clear_caches(self):
        """Clear all color caches"""
        self._event_color_cache.clear()
        self._place_color_cache = {}

    def place_color(self, place_id):
        """Get color for a place"""
        if place_id == "__NO_PLACE__":
            cached = self._place_color_cache.get(place_id)
            if cached:
                return QColor(cached)
            fallback = QColor("#D5D7DD")
            self._place_color_cache[place_id] = fallback.name()
            return fallback

        cached = self._place_color_cache.get(place_id)
        if cached:
            return QColor(cached)

        places_map = getattr(self.timeline_controller, '_places_map', {})
        place = places_map.get(place_id)
        stored = getattr(place, 'timeline_color', None) if place else None
        if stored:
            candidate = QColor(stored)
            if candidate.isValid():
                candidate = self.ensure_readable(candidate, 150.0)
                self._place_color_cache[place_id] = candidate.name()
                return candidate

        actual_count = sum(1 for key in self._place_color_cache if key != "__NO_PLACE__")
        palette_index = actual_count % len(self.EVENT_COLOR_PALETTE)
        base_color = QColor(self.EVENT_COLOR_PALETTE[palette_index])
        offset = actual_count // len(self.EVENT_COLOR_PALETTE)
        for _ in range(offset):
            base_color = base_color.lighter(108)
        base_color = self.ensure_readable(base_color, 150.0)
        if place:
            place.timeline_color = base_color.name()
        self._place_color_cache[place_id] = base_color.name()
        return base_color

    def event_color(self, event, place_color= None):
        """Get color for an event, based on place color"""
        event_id = getattr(event, 'id', None)
        # Use place color if available
        if place_color is not None and place_color.isValid():
            color = QColor(place_color)
            color = self.ensure_color(color)
            if event_id:
                self._event_color_cache[event_id] = color
            setattr(event, 'timeline_color', color.name())
            return color

        if event_id and event_id in self._event_color_cache:
            color = QColor(self._event_color_cache[event_id])
            setattr(event, 'timeline_color', color.name())
            return color

        stored = getattr(event, 'timeline_color', None)
        if stored:
            candidate = QColor(stored)
            if candidate.isValid():
                candidate = self.ensure_color(candidate)
                if event_id:
                    self._event_color_cache[event_id] = candidate
                setattr(event, 'timeline_color', candidate.name())
                return candidate
        # Generate new color from palette
        palette_index = len(self._event_color_cache) % len(self.EVENT_COLOR_PALETTE)
        variant = QColor(self.EVENT_COLOR_PALETTE[palette_index])
        offset = len(self._event_color_cache) // len(self.EVENT_COLOR_PALETTE)
        for _ in range(offset):
            variant = variant.lighter(110)
        variant = self.ensure_color(variant)
        if event_id:
            self._event_color_cache[event_id] = variant
        setattr(event, 'timeline_color', variant.name())
        return variant

    def ensure_color(self, color):
        """Make sure the event color is bright enough and easy to read."""
        color = self.ensure_readable(color, 170.0)
        if self.color_luminance(color) > 220:
            color = color.darker(110)
        return color

    def safe_char_color(self, color):
        """for character elements"""
        return self.ensure_readable(color, 90.0)

    def char_label_color(self, color, background= None):
        """Return a text color that is easy to read against the given background color."""
        if not color.isValid():
            return QColor("#f0f0f0")
        if background is None or not background.isValid():
            background = color
        dark_mode = getattr(self.timeline_controller.main_controller, "dark_mode_enabled", False)
        bg_luminance = self.color_luminance(background)

        if bg_luminance >= 205:
            target_luminance = 30 if not dark_mode else 45
        elif bg_luminance <= 80:
            target_luminance = 235
        elif dark_mode and bg_luminance < 150:
            target_luminance = 220
        else:
            target_luminance = 200 if dark_mode and bg_luminance < 180 else 60
        return self._with_luminance(color, target_luminance)

    def ensure_readable(self, color, min_luminance):
        """Make sure the color is bright enough to be readable."""
        if not color.isValid():
            return QColor("#CCCCCC")
        if color == QColor(Qt.black):
            color = QColor("#444444")

        attempts = 0
        while self.color_luminance(color) < min_luminance and attempts < 8:
            color = color.lighter(120)
            attempts += 1
        if self.color_luminance(color) < min_luminance:
            fallback = 200 if min_luminance > 120 else 150
            hue = color.hue()
            if hue < 0:
                return QColor(fallback, fallback, fallback)
            color = QColor.fromHsl(hue, 80, fallback)
        return color

    def _with_luminance(self, color, target_luminance):
        """Return a color with the same tone but lighter or darker."""
        target = max(0, min(255, int(target_luminance)))
        hue = color.hslHue()
        sat = color.hslSaturation()
        if hue < 0:
            return QColor(target, target, target)
        if sat < 0:
            sat = 0
        return QColor.fromHsl(hue, sat, target)

    @staticmethod
    def color_luminance(color):
        """Find the visible brightness level of a color."""
        r, g, b = color.red(), color.green(), color.blue()
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

def build_dark_palette(base_palette):
    """Return a darker version of the given palette for dark mode."""
    if base_palette is None:
        return None
    palette = QPalette(base_palette)
    window_color = QColor(45, 45, 45)
    base_color = QColor(30, 30, 30)
    alt_base_color = QColor(40, 40, 40)

    palette.setColor(QPalette.Window, window_color)
    palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
    palette.setColor(QPalette.Base, base_color)
    palette.setColor(QPalette.AlternateBase, alt_base_color)
    palette.setColor(QPalette.ToolTipBase, QColor(65, 65, 65))
    palette.setColor(QPalette.ToolTipText, QColor(240, 240, 240))
    palette.setColor(QPalette.Text, QColor(230, 230, 230))
    palette.setColor(QPalette.Button, window_color)
    palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
    palette.setColor(QPalette.BrightText, QColor(255, 80, 80))
    palette.setColor(QPalette.Highlight, QColor(90, 120, 200))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    # Ensure frame match the window background in dark mode
    palette.setColor(QPalette.Dark, window_color)
    palette.setColor(QPalette.Mid, window_color)
    palette.setColor(QPalette.Shadow, window_color)
    palette.setColor(QPalette.Midlight, window_color)
    palette.setColor(QPalette.Light, window_color)
    return palette
