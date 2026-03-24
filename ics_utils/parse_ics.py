from ics import Calendar
import hashlib
import pytz

def parse_ics(ics_text: str):
    cal = Calendar(ics_text)
    events = []

    # Always convert ICS timestamps into America/New_York
    local_tz = pytz.timezone("America/New_York")

    for e in cal.events:
        raw_uid = e.uid or ""
        safe_uid = hashlib.sha256(raw_uid.encode("utf-8")).hexdigest()[:32]

        # Extract raw datetime objects from ics.py
        start_dt = e.begin.datetime
        end_dt = e.end.datetime

        # --- FIXED TIMEZONE LOGIC ---
        # If the ICS timestamp has tzinfo (e.g., +00:00), treat it as UTC and convert.
        # If it is naive, assume it is already local.
        if start_dt.tzinfo is not None:
            start_local = start_dt.astimezone(local_tz)
        else:
            start_local = local_tz.localize(start_dt)

        if end_dt.tzinfo is not None:
            end_local = end_dt.astimezone(local_tz)
        else:
            end_local = local_tz.localize(end_dt)

        events.append({
            "event_id": safe_uid,
            "start": start_local,
            "end": end_local,
            "summary": e.name,
            "location": e.location,
            "description": e.description,
        })

    return events
