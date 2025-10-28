from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtGui import QTransform

class TimelineScene(QGraphicsScene):
    """mouse click events"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        
    def mousePressEvent(self, event):
        if event.button() != Qt.RightButton:
            super().mousePressEvent(event)
            return
        click_position = event.scenePos()
        item = self.itemAt(click_position, QTransform())
        if item is None:
            super().mousePressEvent(event)  # empty area
            return
        item_data = item.data(0)

        if not isinstance(item_data, dict):
            super().mousePressEvent(event)  
            return
        role = item_data.get('role')
        kind = item_data.get('kind')
        handled = False
        if role == 'label' and kind == 'place':
            handled = self.controller.handle_label_menu(click_position, item_data)
        elif kind in ('event', 'character'):
            handled = self.controller.handle_item_menu(click_position, item_data)
        if handled:
            event.accept()
        else:
            super().mousePressEvent(event)