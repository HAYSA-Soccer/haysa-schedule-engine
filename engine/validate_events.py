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
        try:
            loc_raw = e.get("location") or ""

            # Try to extract ICS code from "CODE, Description"
            # e.g. "H-SJ3, Holbrook Sean Joyce 3"
            ics_code = ""
            if "," in loc_raw:
                ics_code = loc_raw.split(",")[0].strip()
            else:
                ics_code = loc_raw.strip()

            if not ics_code:
                raise ValueError(f"Missing ICS field code in location: {loc_raw}")

            # Column 4 in Events sheet = ICS code
            e["field"] = ics_code

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
