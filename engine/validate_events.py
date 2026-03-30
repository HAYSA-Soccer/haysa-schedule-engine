from datetime import datetime
import yaml
import os

def extract_abbreviation_from_location(loc: str):
    """
    Convert ICS location strings into the field abbreviations
    used by the Apps Script backend (H-HST1, H-HST2, H-BP1A, etc.)
    """
    if not loc:
        return None

    cleaned = loc.lower()

    # -------------------------
    # HOLBROOK TURF COMPLEX
    # -------------------------
    if "turf 1" in cleaned:
        return "H-HST1"
    if "turf 2" in cleaned:
        return "H-HST2"
    if "turf" in cleaned:
        return "H-HST"   # full field

    # -------------------------
    # BROOKVILLE COMPLEX
    # -------------------------
    if "brookville" in cleaned and "1" in cleaned:
        return "H-BP1A"   # adjust if needed
    if "brookville" in cleaned and "2" in cleaned:
        return "H-BP2A"
    if "brookville" in cleaned:
        return "H-B"      # full field

    # -------------------------
    # SUMNER
    # -------------------------
    if "sumner" in cleaned and "1" in cleaned:
        return "H-Su1"
    if "sumner" in cleaned and "2" in cleaned:
        return "H-Su2"

    # -------------------------
    # SEAN JOYCE
    # -------------------------
    if "sean joyce" in cleaned and "3" in cleaned:
        return "H-SJ3"
    if "sean joyce" in cleaned and "4" in cleaned:
        return "H-SJ4"

    # -------------------------
    # AVON BUTLER
    # -------------------------
    if "butler" in cleaned and "1" in cleaned:
        return "A-B1"
    if "butler" in cleaned and "2" in cleaned:
        return "A-B2"
    if "butler" in cleaned and "3" in cleaned:
        return "A-B3"
    if "butler" in cleaned and "4" in cleaned:
        return "A-B4"

    return None


def validate_events(events):
    """
    Validates parsed ICS events and returns:
    - valid_events: events ready for calendar sync
    - errors: list of validation issues
    """

    valid = []
    errors = []

    # Load field mapping from YAML (still used for games)
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

        # -----------------------------
        # PRACTICES → USE ICS LOCATION
        # -----------------------------
        if is_practice:
            abbr = extract_abbreviation_from_location(loc)
            if abbr:
                e["field"] = abbr
                valid.append(e)
                continue
            # fallback to YAML if needed

        # -----------------------------
        # GAMES → USE YAML MAPPING
        # -----------------------------
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

        if not mapped:
            errors.append(f"{eid}: Unknown field location '{loc}'")
            continue

        e["field"] = mapped
        valid.append(e)

    return valid, errors
