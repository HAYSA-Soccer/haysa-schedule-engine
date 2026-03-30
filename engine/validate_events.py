from datetime import datetime
import yaml
import os

def extract_surface_from_location(loc: str):
    """
    Extracts surface-level field info from ICS location strings.
    Examples:
      "H-HST1" → "TURF1"
      "H-HST 1" → "TURF1"
      "Turf 1" → "TURF1"
      "Holbrook High School Turf Field 1" → "TURF1"
    """
    if not loc:
        return None

    cleaned = loc.replace(" ", "").upper()

    # TURF surfaces
    if "H-HST1" in cleaned or "TURF1" in cleaned:
        return "TURF1"
    if "H-HST2" in cleaned or "TURF2" in cleaned:
        return "TURF2"

    # BROOKVILLE surfaces
    if "H-B1" in cleaned or "BROOKVILLE1" in cleaned:
        return "BROOKVILLE1"
    if "H-B2" in cleaned or "BROOKVILLE2" in cleaned:
        return "BROOKVILLE2"

    return None


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

        summary = (e.get("summary") or "").lower()
        is_practice = "practice" in summary
        is_game = "vs" in summary

        # -----------------------------
        # PRACTICE: Use ICS surface directly
        # -----------------------------
        if is_practice:
            surface = extract_surface_from_location(loc)
            if surface:
                e["field"] = surface
                valid.append(e)
                continue
            # If no surface match, fall back to YAML mapping

        # -----------------------------
        # GAME or fallback: YAML mapping
        # -----------------------------
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

        e["field"] = mapped
        valid.append(e)

    return valid, errors
