from datetime import datetime
import yaml
import os

def validate_events(events):
    """
    Validates parsed ICS events and returns:
    - valid_events: events ready for calendar sync
    - errors: list of validation issues
    """

    valid = []
    errors = []

    # Load field mapping from YAML
    try:
        with open("config/fields.yaml") as f:
            fields_config = yaml.safe_load(f).get("fields", {})
    except Exception as ex:
        return [], [f"Failed to load fields.yaml: {ex}"]

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

        # Try to match ICS location against each field's patterns
        mapped = None

        for field_name, cfg in fields_config.items():
            patterns = cfg.get("match", [])
            for pattern in patterns:
                if pattern.upper() in loc:
                    mapped = field_name
                    break
            if mapped:
                break

        if not mapped:
            errors.append(f"{eid}: Unknown field location '{loc}'")
            continue

        # Store mapped field
        e["field"] = mapped
        valid.append(e)

    return valid, errors
