import os
from ics.fetch_ics import fetch_ics
from ics.parse_ics import parse_ics
from engine.sheets import get_sheet, write_events_to_sheet

def main():
    ics_url = os.environ["ICS_URL"]
    sheet_id = os.environ["GOOGLE_SHEET_ID"]

    print("Fetching ICS...")
    ics_text = fetch_ics(ics_url)

    print("Parsing ICS...")
    events = parse_ics(ics_text)

    print(f"Parsed {len(events)} events")

    print("Writing to Google Sheet...")
    sheet = get_sheet(sheet_id)
    write_events_to_sheet(sheet, events)

    print("Done.")

if __name__ == "__main__":
    main()
