import os
from ics_utils.fetch_ics import fetch_ics
from ics_utils.parse_ics import parse_ics
from engine.sheets import get_sheet, write_events_to_sheet
from engine.validate_events import validate_events

def main():
    ics_url = os.environ["ICS_URL"]
    sheet_id = os.environ["GOOGLE_SHEET_ID"]

    print("Fetching ICS...")
    ics_text = fetch_ics(ics_url)

    print("Parsing ICS...")
    events = parse_ics(ics_text)

    print(f"Parsed {len(events)} events")

    print("Validating events...")
    valid, errors = validate_events(events)

    print(f"Valid events: {len(valid)}")
    print(f"Errors: {len(errors)}")

    if errors:
        print("Validation errors:")
        for err in errors:
            print(" -", err)

    print("Writing to Google Sheet...")
    sheet = get_sheet(sheet_id)
    write_events_to_sheet(sheet, valid)

    print("Done.")

if __name__ == "__main__":
    main()
