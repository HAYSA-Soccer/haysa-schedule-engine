from ics import Calendar
from datetime import datetime
import hashlib
import pytz

def parse_ics(ics_text: str):
    """
    Parses ICS text and returns a list of event dicts.
    Ensures all times are interpreted in LOCAL timezone.
    """
    cal = Calendar(ics_text)
    events = []

    # Your local timezone (Eastern)
    local_tz = pytz.timezone("America/New_York")

    for e in cal.events:
        # Generate a safe, deterministic Google‑Calendar‑compatible event ID
        raw_uid = e.uid or ""
        safe_uid = hashlib.sha256(raw_uid.encode("utf-8")).hexdigest()[:32]

        # Convert ICS naive datetimes → local timezone → UTC
        start_local = local_tz.localize(e.begin.datetime)
        end_local = local_tz.localize(e.end.datetime)

        # Convert to UTC ISO strings for Sheets
        start_utc = start_local.astimezone(pytz.utc)
        end_utc = end_local.astimezone(pytz.utc)

        events.append({
            "event_id": safe_uid,
            "start": start_utc.isoformat(),
            "end": end_utc.isoformat(),
            "summary": e.name,
            "location": e.location,
            "description": e.description,
        })

    return events
