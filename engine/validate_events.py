
from datetime import datetime

def validate_events(events):
    """
    Validates parsed ICS events and returns:
    - valid_events: events ready for calendar sync
    - errors: list of validation issues
    """

    valid = []
    errors = []

    for e in events:
        eid = e.get("event_id")

        # Check required fields
        if not e.get("start") or not e.get("end"):
            errors.append(f"{eid}: Missing start or end time")
            continue

        if e["end"] <= e["start"]:
            errors.append(f"{eid}: End time is before start time")
            continue

        if not e.get("summary"):
            errors.append(f"{eid}: Missing summary")
            continue

        # Normalize location
        loc = (e.get("location") or "").strip().upper()

        if not loc:
            errors.append(f"{eid}: Missing location")
            continue

        # Basic field mapping (expand later)
        field_map = {
            "SUMNER": "SUMNER",
            "BUTLER": "BUTLER",
            "TURF": "TURF",
        }

        mapped = None
        for key, val in field_map.items():
            if key in loc:
                mapped = val
                break

        if not mapped:
            errors.append(f"{eid}: Unknown field location '{loc}'")
            continue

        e["field"] = mapped
        valid.append(e)

    return valid, errors
