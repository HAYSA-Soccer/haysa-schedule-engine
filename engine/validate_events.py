import re
from datetime import datetime

# ============================================================
# VALIDATE + NORMALIZE EVENTS FROM parse_ics.py
# ============================================================

def validate_events(events):
    valid = []
    errors = []

    for e in events:
        try:
            # ------------------------------------------------------------
            # 1. Extract ICS field code from the ICS location string
            # ------------------------------------------------------------
            # Example ICS location:
            #   "H-SJ3, Holbrook Sean Joyce Field"
            #
            # We MUST extract "H-SJ3" because the Google Apps Script backend
            # depends on this exact ICS FIELD CODE for FieldMapping lookup.
            # ------------------------------------------------------------
            loc_raw = e.get("location") or ""
            ics_code = loc_raw.split(",")[0].strip()  # <-- CRITICAL FIX

            if not ics_code:
                raise ValueError(f"Missing ICS field code in location: {loc_raw}")

            # ------------------------------------------------------------
            # 2. Store ICS FIELD CODE in `field` (column 4 in Events sheet)
            # ------------------------------------------------------------
            e["field"] = ics_code

            # ------------------------------------------------------------
            # 3. Store full ICS location text for display (optional)
            # ------------------------------------------------------------
            e["field_display"] = loc_raw.strip()

            # ------------------------------------------------------------
            # 4. Derive canonical field group (SUMNER/SEAN JOYCE, TURF, etc.)
            # ------------------------------------------------------------
            # This matches your YAML logic and your Apps Script canonical names.
            # ------------------------------------------------------------
            canonical = derive_canonical_from_ics(ics_code)
            e["field_group"] = canonical

            # ------------------------------------------------------------
            # 5. Basic validation
            # ------------------------------------------------------------
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


# ============================================================
# CANONICAL FIELD GROUP LOGIC
# ============================================================

def derive_canonical_from_ics(ics_code: str):
    """
    Convert ICS field codes into canonical field groups.
    This matches your FieldMapping + FieldComplexes logic.
    """

    code = ics_code.upper()

    # SUMNER / SEAN JOYCE
    if code.startswith("H-SJ") or code.startswith("H-SU"):
        return "SUMNER/SEAN JOYCE"

    # BUTLER
    if code.startswith("H-BU"):
        return "BUTLER"

    # TURF
    if code.startswith("H-TU"):
        return "TURF"

    # BROOKVILLE (example — adjust if needed)
    if code.startswith("H-BR"):
        return "BROOKVILLE"

    # Default fallback
    return "UNKNOWN"
