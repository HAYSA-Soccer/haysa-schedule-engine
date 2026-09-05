import os
from ics_utils.fetch_ics import fetch_ics
from ics_utils.parse_ics import parse_ics
from engine.validate_events import validate_events
from engine.sheets import upsert_events_to_sheet, load_field_mapping   # ⭐ load mapping

def main():
    ics_url = os.environ["ICS_URL"]

    print("Fetching ICS...")
    ics_text = fetch_ics(ics_url)

    print("Parsing ICS...")
    events = parse_ics(ics_text)

    print("Loading FieldMapping...")
    field_mapping = load_field_mapping()   # ⭐ REQUIRED for new validator

    print("Validating events...")
    valid, errors = validate_events(events, field_mapping)  # ⭐ pass mapping

    print(f"Valid events: {len(valid)}")
    print(f"Errors: {len(errors)}")

    if errors:
        print("Validation errors:")
        for err in errors:
            print(" -", err)

    print("Updating Google Sheet...")
    upsert_events_to_sheet(valid)
    print("Sheet updated.")

    print("Done.")

if __name__ == "__main__":
    main()
