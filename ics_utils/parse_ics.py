from ics import Calendar
from datetime import datetime
import hashlib

def parse_ics(ics_text: str):
    """
    Parses ICS text and returns a list of event dicts.
    """
    cal = Calendar(ics_text)
    events = []

    for e in cal.events:
        # Generate a safe, deterministic Google‑Calendar‑compatible event ID
        raw_uid = e.uid or ""
        safe_uid = hashlib.sha256(raw_uid.encode("utf-8")).hexdigest()[:32]

        events.append({
            "event_id": safe_uid,
            "start": e.begin.datetime,
            "end": e.end.datetime,
            "summary": e.name,
            "location": e.location,
            "description": e.description,
        })

    return events
