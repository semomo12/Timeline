from datetime import datetime

class TimelineHandler:
    """Handles timeline data"""

    def __init__(self, main_controller):
        self.main = main_controller

    def get_events(self, mode):
        """Get events for timeline"""
        events = []
        project = self.main.project
        
        if mode == "day_sequence":
            #numbers instead of real dates
            current_day = 1

            for event in project.events:
                start_day = getattr(event, 'day_index', None)
                if not start_day or start_day <= 0:
                    start_day = current_day
                    current_day += 1

                end_day = getattr(event, 'day_index_end', None)
                if not end_day or end_day < start_day:
                    end_day = start_day

                display_mode = getattr(event, 'display_mode', 'span')
                if display_mode == "point":
                    end_day = start_day

                event.day_index = start_day
                event.day_index_end = end_day
                event.timeline_mode = "day_sequence"
                event.display_mode = display_mode
                event.start_date = f"Day {start_day}"
                event.end_date = f"Day {end_day}"
                events.append({
                    'event': event,
                    'start_day': start_day,
                    'end_day': end_day,
                    'is_point': display_mode == "point",
                    'sequence_start': start_day,
                    'sequence_end': end_day,
                    'start': start_day, 
                    'end': end_day
                })
                current_day = max(current_day, end_day + 1)

            return events

        else:
            #real dates
            for event in project.events:
                start = self.parse_date(event.start_date)
                if not start:
                    # Use today as default start date
                    start = datetime.today()
                    event.start_date = start.date().isoformat()

                end = self.parse_date(event.end_date)
                display_mode = getattr(event, 'display_mode', 'span')

                if display_mode == "point" or not end:
                    end = start
                    event.end_date = event.start_date
                elif end < start:
                    end = start
                    event.end_date = event.start_date

                event.timeline_mode = "calendar"
                event.day_index = None
                event.day_index_end = None
                event.display_mode = display_mode
                events.append({
                    'event': event,
                    'start': start,
                    'end': end,
                    'is_point': display_mode == "point"
                })

            return events

    def parse_date(self, date_string):
        """date string to date object"""
        if not date_string:
            return None

        date_string = date_string.strip()
        if not date_string:
            return None
        formats = [
            "%Y-%m-%d",      # 2025-10-31
            "%Y/%m/%d",      # 2025/10/31
            "%Y-%m-%dT%H:%M" # 2025-10-31T00:00
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except:
                continue

        return None

    def _get_names_by_ids(self, items, item_ids):
        """Get names from list of items"""
        names = []
        for item_id in item_ids:
            for item in items:
                if item.id == item_id:
                    names.append(item.name)
                    break
        return names

    def get_character_names(self, character_ids):
        """Get character names"""
        return self._get_names_by_ids(self.main.project.characters, character_ids)

    def get_event_names(self, event_ids):
        """Get event names"""
        return self._get_names_by_ids(self.main.project.events, event_ids)

    def get_place_names(self, place_ids):
        """Get place names"""
        return self._get_names_by_ids(self.main.project.places, place_ids)
