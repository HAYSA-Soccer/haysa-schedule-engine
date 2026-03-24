from ics import Calendar
from datetime import datetime
import hashlib
import pytz

def parse_ics(ics_text: str):
    cal = Calendar(ics_text)
    events = []

    local_tz = pytz.timezone("America/New_York")

    for e in cal.events:
        raw_uid = e.uid or ""
        safe_uid = hashlib.sha256(raw_uid.encode("utf-8")).hexdigest()[:32]

        # --- FIX: handle naive vs aware datetimes ---
        start_dt = e.begin.datetime
        end_dt = e.end.datetime

        # If datetime has no tzinfo → treat as LOCAL time
        if start_dt.tzinfo is None:
            start_local = local_tz.localize(start_dt)
        else:
            start_local = start_dt.astimezone(local_tz)

        if end_dt.tzinfo is None:
            end_local = local_tz.localize(end_dt)
        else:
            end_local = end_dt.astimezone(local_tz)

        # Convert to UTC for Sheets
        start_utc = start_local.astimezone(pytz.utc)
        end_utc = end_local.astimezone(pytz.utc)

        events.append({
            "event_id": safe_uid,
            "start": start_utc,   # datetime, not string
            "end": end_utc,       # datetime, not string
            "summary": e.name,
            "location": e.location,
            "description": e.description,
        })

    return events
