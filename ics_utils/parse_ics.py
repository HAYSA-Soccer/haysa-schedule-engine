from ics import Calendar
from datetime import datetime

def parse_ics(ics_text: str):
    """
    Parses ICS text and returns a list of event dicts.
    """
    cal = Calendar(ics_text)
    events = []

    for e in cal.events:
        events.append({
            "event_id": e.uid,
            "start": e.begin.datetime,
            "end": e.end.datetime,
            "summary": e.name,
            "location": e.location,
            "description": e.description,
        })

    return events
