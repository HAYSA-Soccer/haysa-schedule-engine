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

    # Load YAML for game mapping (optional)
    try:
        with open("config/fields.yaml") as f:
            fields_config = yaml.safe_load(f).get("fields", {})
    except Exception as ex:
        return [], [f"Failed to load fields.yaml: {ex}"]

    for e in events:
        eid = e.get("event_id")

        # Required fields
        if not e.get("start") or not e.get("end"):
            errors.append(f"{eid}: Missing start or end time")
            continue

        if e["end"] <= e["start"]:
            errors.append(f"{eid}: End time is before start time")
            continue

        if not e.get("summary"):
            errors.append(f"{eid}: Missing summary")
            continue

        loc = (e.get("location") or "").strip()
        if not loc:
            errors.append(f"{eid}: Missing location")
            continue

        summary = (e.get("summary") or "").lower()
        is_practice = "practice" in summary
        is_game = "vs" in summary

        # ----------------------------------------------------
        # PRACTICES → USE ICS LOCATION EXACTLY AS PROVIDED
        # ----------------------------------------------------
        if is_practice:
            e["field"] = loc
            valid.append(e)
            continue

        # ----------------------------------------------------
        # GAMES → OPTIONAL YAML MAPPING (if desired)
        # ----------------------------------------------------
        mapped = None
        loc_upper = loc.upper()

        for field_name, cfg in fields_config.items():
            patterns = cfg.get("match", [])
            for pattern in patterns:
                if pattern.upper() in loc_upper:
                    mapped = field_name
                    break
            if mapped:
                break

        # If YAML mapping fails, fall back to raw ICS location
        if mapped:
            e["field"] = mapped
        else:
            e["field"] = loc

        valid.append(e)

    return valid, errors
