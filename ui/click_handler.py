from PySide6.QtWidgets import QMenu

class TimelineClickHandler:
    """Handles clicks and menus"""

    def __init__(self, timeline_controller):
        self.timeline_controller = timeline_controller

    def click(self, data):
        kind = data.get('kind')
        item_id = data.get('id')
        if kind == 'event' and item_id in self.timeline_controller._events_map:
            self.timeline_controller.info_dialogs.show_event(
                self.timeline_controller._events_map[item_id]
            )
            return True
        if kind == 'character' and item_id in self.timeline_controller._characters_map:
            self.timeline_controller.info_dialogs.show_char(
                self.timeline_controller._characters_map[item_id]
            )
            return True
        if kind == 'place':
            if item_id == "__NO_PLACE__":
                self.timeline_controller.info_dialogs.show_dialog("Unplaced Events", [
                    ("Description", "Events listed under this lane have no associated place yet.")
                ])
                return True
            if item_id in self.timeline_controller._places_map:
                self.timeline_controller.info_dialogs.show_place(
                    self.timeline_controller._places_map[item_id]
                )
                return True
        return False

    def handle_label_menu(self, scene_pos, data):
        if not isinstance(data, dict):
            return False
        if data.get('kind') != 'place' or data.get('role') != 'label':
            return False
        menu = QMenu()
        show_action = menu.addAction("Show")
        edit_action = menu.addAction("Edit")

        view = getattr(self.timeline_controller.main_controller, 'viewTimeline', None)
        if not view:
            return False
        view_point = view.mapFromScene(scene_pos)
        global_point = view.viewport().mapToGlobal(view_point)
        picked = menu.exec(global_point)
        if picked is None:
            return True
        if picked == show_action:
            place_id = data.get('id')
            if place_id == "__NO_PLACE__":
                self.timeline_controller.info_dialogs.show_dialog("Unplaced Events", [
                    ("Description", "Events listed under this lane have no associated place yet.")
                ])
            elif place_id in self.timeline_controller._places_map:
                self.timeline_controller.info_dialogs.show_place(
                    self.timeline_controller._places_map[place_id]
                )
            return True
        if picked == edit_action:
            place_id = data.get('id')
            if hasattr(self.timeline_controller.main_controller, 'place_controller') and place_id:
                self.timeline_controller.main_controller.place_controller.edit_by_id(place_id)
            return True
        return True

    def handle_item_menu(self, scene_pos, data):
        if not isinstance(data, dict):
            return False
        kind = data.get('kind')
        item_id = data.get('id')
        if kind not in ('event', 'character') or not item_id:
            return False
        menu = QMenu()
        show_action = menu.addAction("Show")
        edit_action = menu.addAction("Edit")
        add_char_action = None
        if kind == 'event':
            add_char_action = menu.addAction("Add Character")
        view = getattr(self.timeline_controller.main_controller, 'viewTimeline', None)
        if not view:
            return False
        view_point = view.mapFromScene(scene_pos)
        global_point = view.viewport().mapToGlobal(view_point)
        picked = menu.exec(global_point)
        if picked is None:
            return True
        if picked == show_action:
            if kind == 'event' and item_id in self.timeline_controller._events_map:
                self.timeline_controller.info_dialogs.show_event(
                    self.timeline_controller._events_map[item_id]
                )
            elif kind == 'character' and item_id in self.timeline_controller._characters_map:
                self.timeline_controller.info_dialogs.show_char(
                    self.timeline_controller._characters_map[item_id]
                )
            return True

        if picked == edit_action:
            if kind == 'event':
                if hasattr(self.timeline_controller.main_controller, 'event_controller'):
                    self.timeline_controller.main_controller.event_controller.edit_by_id(item_id)
                elif hasattr(self.timeline_controller.main_controller, 'edit_event'):
                    self.timeline_controller.main_controller.event_controller.edit()
            elif kind == 'character':
                if hasattr(self.timeline_controller.main_controller, 'character_controller'):
                    self.timeline_controller.main_controller.character_controller.edit_by_id(item_id)
                elif hasattr(self.timeline_controller.main_controller, 'edit_character'):
                    self.timeline_controller.main_controller.character_controller.edit()
            return True

        if picked == add_char_action and kind == 'event':
            if hasattr(self.timeline_controller.main_controller, 'character_controller'):
                char_ctrl = self.timeline_controller.main_controller.character_controller
                char_ctrl.add_to_event(item_id)
            return True

        return True
