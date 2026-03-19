import os
from ics_utils.fetch_ics import fetch_ics
from ics_utils.parse_ics import parse_ics
from engine.validate_events import validate_events
from engine.sync_calendar import sync_events_to_calendar

def main():
    ics_url = os.environ["ICS_URL"]

    print("Fetching ICS...")
    ics_text = fetch_ics(ics_url)

    print("Parsing ICS...")
    events = parse_ics(ics_text)

    print("Validating events...")
    valid, errors = validate_events(events)

    print(f"Valid events: {len(valid)}")
    print(f"Errors: {len(errors)}")

    # 🔍 DEBUG: Which repo is this workflow running in?
    print("DEBUG: running in repo =", os.environ.get("GITHUB_REPOSITORY"))

    # 🔍 DEBUG: What EXACT value is GitHub passing for CAL_TURF?
    print("DEBUG: CAL_TURF repr =", repr(os.environ.get("CAL_TURF")))
    print("DEBUG: CAL_TURF length =", len(os.environ.get("CAL_TURF", "")))

    # Group events by field
    by_field = {}
    for e in valid:
        field = e["field"]
        by_field.setdefault(field, []).append(e)

    # Sync each field calendar
    # Sync each field calendar
    for field, evs in by_field.items():
        env_name = f"CAL_{field}"
        val = os.environ.get(env_name, "")

        # 🔍 NEW DEBUG LINES
        print(f"DEBUG: {env_name} length =", len(val))
        print(f"DEBUG: {env_name} startswith =", val[:5])
        print(f"DEBUG: {env_name} endswith =", val[-5:])

        if not val:
            print(f"Skipping {field}: no calendar secret found")
            continue
    
        print(f"Syncing {field} ({val}) with {len(evs)} events...")
        sync_events_to_calendar(evs, val)

    print("Done.")

if __name__ == "__main__":
    main()
