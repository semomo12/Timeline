from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor

def attach_char_drag(
    char_rect,
    *,
    character,
    source_event,
    get_drop_target,
    validate_move,
    move_to_event,
    move_within_event,
    refresh,
):
    orig_press = char_rect.mousePressEvent
    orig_release = char_rect.mouseReleaseEvent
    drag_info = {
        "dragging": False,
        "start_pos": None,
        "start_scene_pos": None,
        "orig_pos": None,
        "orig_label_pos": None,
    }
    
    def on_press(event):
        if orig_press:
            orig_press(event)
        if event.button() == Qt.LeftButton:
            drag_info["dragging"] = True
            drag_info["start_pos"] = event.pos()
            drag_info["start_scene_pos"] = event.scenePos()
            drag_info["orig_pos"] = char_rect.pos()
            drag_info["orig_z"] = char_rect.zValue()
            if hasattr(char_rect, "_character_label"):
                drag_info["orig_label_pos"] = char_rect._character_label.pos()
                drag_info["orig_label_z"] = char_rect._character_label.zValue()
            char_rect.setCursor(QCursor(Qt.ClosedHandCursor))
            char_rect.setZValue(1000)
            if hasattr(char_rect, "_character_label"):
                char_rect._character_label.setZValue(1001)

    def on_release(event):
        if event.button() == Qt.LeftButton and drag_info.get("dragging"):
            drag_info["dragging"] = False
            drag_info["start_scene_pos"] = None
            char_rect.setCursor(QCursor(Qt.OpenHandCursor))
            char_rect.setZValue(drag_info.get("orig_z", 0))
            if hasattr(char_rect, "_character_label") and "orig_label_z" in drag_info:
                char_rect._character_label.setZValue(drag_info["orig_label_z"])

            drop_target = get_drop_target(char_rect)
            target_event = None
            insert_index = None
            if isinstance(drop_target, dict):
                target_event = drop_target.get("event")
                insert_index = drop_target.get("index")
            else:
                target_event = drop_target
            moved = False
            need_refresh = False
            if target_event and target_event != source_event:
                if validate_move(character, target_event, source_event):
                    try:
                        if move_to_event(character, source_event, target_event, insert_index):
                            print(f"Moved {character.name} from {source_event.name} to {target_event.name}")
                            moved = True
                            need_refresh = True
                    except Exception as error:
                        print(f"Error moving character: {error}")
                else:
                    print(f"Cannot move {character.name} to {target_event.name} - not allowed")
            elif target_event == source_event and target_event is not None:
                try:
                    if move_within_event(character, source_event, insert_index):
                        print(f"Reordered {character.name} in {source_event.name}")
                        moved = True
                        need_refresh = True
                except Exception as error:
                    print(f"Error reordering character: {error}")
            if not moved:
                char_rect.setPos(drag_info["orig_pos"])
                if hasattr(char_rect, "_character_label") and drag_info.get("orig_label_pos"):
                    char_rect._character_label.setPos(drag_info["orig_label_pos"])
                print(f"Character {character.name} returned to original position")
            if orig_release:
                try:
                    orig_release(event)
                except RuntimeError as e:
                    if 'already deleted' not in str(e):
                        raise
            if need_refresh:
                refresh()
            return
        if orig_release:
            try:
                orig_release(event)
            except RuntimeError as e:
                if 'already deleted' not in str(e):
                    raise

    char_rect.mousePressEvent = on_press
    char_rect.mouseReleaseEvent = on_release
