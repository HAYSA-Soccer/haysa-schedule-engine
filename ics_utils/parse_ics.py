from ics import Calendar
from datetime import datetime
import hashlib
import pytz

def parse_ics(ics_text: str):
    cal = Calendar(ics_text)
    events = []

    local_tz = pytz.timezone("America/New_York")

    # IDs we want to inspect
    debug_ids = {
        "5620be3c92ce1ccc914c853e9051171b",
        "80816a59e641cb9e0672b23791d37c59",
        "c12186c4e9b8f1b4892c50eeb614cc78",
    }

    for e in cal.events:
        raw_uid = e.uid or ""
        safe_uid = hashlib.sha256(raw_uid.encode("utf-8")).hexdigest()[:32]

        # --- DEBUG BLOCK: print raw ICS info BEFORE any conversion ---
        if safe_uid in debug_ids:
            print("\n================ RAW ICS EVENT ================")
            print("event_id:", safe_uid)
            print("SUMMARY:", e.name)
            print("LOCATION:", e.location)
            print("BEGIN (ics.py object):", e.begin, "repr:", repr(e.begin))
            print("END   (ics.py object):", e.end,   "repr:", repr(e.end))
            print("BEGIN.datetime:", e.begin.datetime, "tzinfo:", e.begin.datetime.tzinfo)
            print("END.datetime:  ", e.end.datetime,   "tzinfo:", e.end.datetime.tzinfo)
            print("==============================================\n")

        # --- FIX: handle naive vs aware datetimes ---
        start_dt = e.begin.datetime
        end_dt = e.end.datetime

        # Convert ICS datetime → LOCAL Eastern Time
        if start_dt.tzinfo is None:
            start_local = local_tz.localize(start_dt)
        else:
            start_local = start_dt.astimezone(local_tz)

        if end_dt.tzinfo is None:
            end_local = local_tz.localize(end_dt)
        else:
            end_local = end_dt.astimezone(local_tz)

        # Store LOCAL times directly
        events.append({
            "event_id": safe_uid,
            "start": start_local,
            "end": end_local,
            "summary": e.name,
            "location": e.location,
            "description": e.description,
        })

    return events
