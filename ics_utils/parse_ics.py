from ics import Calendar
from datetime import datetime
import re

def parse_ics(ics_text: str):
    """
    Parses ICS text and returns a list of event dicts.
    """
    cal = Calendar(ics_text)
    events = []

    for e in cal.events:
        # Sanitize UID for Google Calendar compatibility
        raw_uid = e.uid or ""
        safe_uid = re.sub(r"[^A-Za-z0-9_-]", "-", raw_uid)

        events.append({
            "event_id": safe_uid,
            "start": e.begin.datetime,
            "end": e.end.datetime,
            "summary": e.name,
            "location": e.location,
            "description": e.description,
        })

    return events
