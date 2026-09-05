from datetime import datetime

def extract_ics_code_from_location(loc_raw, field_mapping):
    """
    Match ICS location text against FieldMapping.ics_match entries.
    Returns the correct ICS abbreviation (e.g., H-SJ3).
    """

    loc = (loc_raw or "").strip().lower()

    for abbr, row in field_mapping.items():
        matches = row.get("ics_match", "")
        for m in matches.split(","):
            if m.strip().lower() in loc:
                return abbr

    return None


def validate_events(events, field_mapping):
    """
    Validates parsed ICS events and enriches them with:
    - field (ICS abbreviation)
    - field_display (raw ICS location)
    - field_group (canonical field)
    """

    valid = []
    errors = []

    for e in events:
        try:
            loc_raw = e.get("location") or ""

            # ⭐ CRITICAL FIX: use ics_match to find the correct ICS code
            ics_code = extract_ics_code_from_location(loc_raw, field_mapping)
            if not ics_code:
                raise ValueError(f"Could not map ICS location: {loc_raw}")

            # Column 4 MUST be the ICS abbreviation
            e["field"] = ics_code

            # Optional display field
            e["field_display"] = loc_raw.strip()

            # Canonical group comes from FieldMapping
            canonical = field_mapping[ics_code]["canonical_field"]
            e["field_group"] = canonical

            # Required fields
            if not e.get("event_id"):
                raise ValueError("Missing event_id")

            if not isinstance(e.get("start"), datetime):
                raise ValueError("Invalid start datetime")

            if not isinstance(e.get("end"), datetime):
                raise ValueError("Invalid end datetime")

            valid.append(e)

        except Exception as err:
            errors.append(str(err))

    return valid, errors
