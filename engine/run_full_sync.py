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

    # Group events by field
    by_field = {}
    for e in valid:
        field = e["field"]
        by_field.setdefault(field, []).append(e)

    # Sync each field calendar
    for field, evs in by_field.items():
        env_name = f"CAL_{field}"
        if env_name not in os.environ:
            print(f"Skipping {field}: no calendar secret found")
            continue

        cal_id = os.environ[env_name]
        print(f"Syncing {field} ({cal_id}) with {len(evs)} events...")
        sync_events_to_calendar(evs, cal_id)

    print("Done.")

if __name__ == "__main__":
    main()
