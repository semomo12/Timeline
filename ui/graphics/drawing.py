from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem, QGraphicsDropShadowEffect, QGraphicsBlurEffect
from PySide6.QtGui import QBrush, QPen, QFont, QColor, QLinearGradient, QFontMetrics
from PySide6.QtCore import Qt

def draw_event_block(scene, event, x, y, width, height, place_name, participant_list, place_color, filtered_chars=None):
    """Draw event block on timeline scene."""
    event_participants = getattr(event, 'participants', [])
    highlight = False
    if filtered_chars and event_participants:
        for char_id in event_participants:
            if char_id in filtered_chars:
                highlight = True
                break
    if place_color:
        base_color = place_color
    else:
        base_color = QColor("#a0c4ff")

    if highlight:
        base_color = base_color.lighter(140)
        pen_width = 4.0
        pen_color = QColor("#ff4500")
        opacity = 1.0
        blur_radius = 0.0
        shadow_blur = 30.0
        shadow_color = QColor(255, 69, 0, 160)
        shadow_offset = (4, 8)
    else:
        if filtered_chars:
            base_color = base_color.darker(220)
            opacity = 0.25
            blur_radius = 0.0
            shadow_blur = 8.0
            shadow_color = QColor(0, 0, 0, 40)
            shadow_offset = (0, 2)
        else:
            opacity = 1.0
            blur_radius = 0.0
            shadow_blur = 16.0
            shadow_color = QColor(0, 0, 0, 90)
            shadow_offset = (0, 4)
        pen_width = 1.4
        pen_color = base_color.darker(140)
        
    gradient = QLinearGradient(x, y, x, y + height)
    gradient.setColorAt(0.0, base_color.lighter(112))
    gradient.setColorAt(1.0, base_color)
    rect = QGraphicsRectItem(x, y, width, height)
    rect.setBrush(QBrush(gradient))
    pen = QPen(pen_color)
    pen.setWidthF(pen_width)
    rect.setPen(pen)
    rect.setData(0, {'kind': 'event', 'id': getattr(event, 'id', None), 'event': event})
    rect.setFlag(QGraphicsRectItem.ItemIsMovable, False)
    rect.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
    rect.setOpacity(opacity)

    if blur_radius > 0:
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(blur_radius)
        rect.setGraphicsEffect(blur)
    else:
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(shadow_blur)
        shadow.setColor(shadow_color)
        shadow.setOffset(shadow_offset[0], shadow_offset[1])
        rect.setGraphicsEffect(shadow)
    tooltip = [event.name]
    if place_name:
        tooltip.append("Place: " + str(place_name))
    if getattr(event, 'start_date', None):
        tooltip.append("Start: " + str(event.start_date))
    if getattr(event, 'end_date', None):
        tooltip.append("End: " + str(event.end_date))
    if participant_list:
        tooltip.append("Participants: " + ", ".join(participant_list))
    rect.setToolTip("\n".join(tooltip))
    scene.addItem(rect)

    if highlight:
        title_font = QFont("Arial", 12, QFont.Bold)
        text_color = QColor("#000000")
    else:
        title_font = QFont("Arial", 10, QFont.Bold)
        if filtered_chars:
            text_color = QColor("#999999")
        else:
            text_color = QColor("#222222")

    font_metrics = QFontMetrics(title_font)
    max_title_width = int(max(0.0, width - 12.0))
    if max_title_width > 0:
        elided_title = font_metrics.elidedText(event.name, Qt.ElideRight, max_title_width)
    else:
        elided_title = event.name
    title_item = QGraphicsTextItem(elided_title)
    title_item.setFont(title_font)
    title_item.setDefaultTextColor(text_color)
    title_item.setToolTip(event.name)
    title_item.setPos(x + 6, y + 6)
    title_item.setData(0, {'kind': 'event', 'id': getattr(event, 'id', None)})
    title_item.setOpacity(opacity)
    if blur_radius > 0:
        blur_text = QGraphicsBlurEffect()
        blur_text.setBlurRadius(blur_radius)
        title_item.setGraphicsEffect(blur_text)
    scene.addItem(title_item)
    title_rect = title_item.boundingRect()
    return y + 6 + title_rect.height()
