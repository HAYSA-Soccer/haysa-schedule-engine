import json
import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SERVICE_ACCOUNT_INFO = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_KEY"])

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet(sheet_id: str, tab_name="Events"):
    """
    Returns a gspread worksheet object for the specified tab.
    """
    creds = Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(sheet_id)
    return spreadsheet.worksheet(tab_name)


def upsert_events_to_sheet(events):
    """
    UPSERT events into the Events tab of the Master Calendar sheet.
    - Updates rows where event_id already exists
    - Inserts new rows for new event_ids
    """

    sheet_id = os.environ["GOOGLE_SHEET_ID"]
    sheet = get_sheet(sheet_id, "Events")

    # Fetch existing rows (skip header)
    existing = sheet.get_all_values()[1:]

    # Map event_id → row index
    existing_map = {row[0]: idx for idx, row in enumerate(existing)}

    updated_rows = existing[:]  # copy

    for e in events:
        date = e["start"].date().isoformat()
        start_time = e["start"].time().isoformat(timespec="minutes")
        end_time = e["end"].time().isoformat(timespec="minutes")

        row = [
            e["event_id"],
            date,
            start_time,
            end_time,
            e.get("field", ""),
            e.get("type", "game"),
            e.get("team", ""),
            e.get("summary", ""),          # ⭐ NEW: write summary into the sheet
            "ICS",
            "active",
            e.get("validation_status", "OK"),
            ""  # calendar_event_id
        ]

        if e["event_id"] in existing_map:
            # Update existing row
            idx = existing_map[e["event_id"]]
            updated_rows[idx] = row
        else:
            # Insert new row
            updated_rows.append(row)

    # Write back (header + rows)
    header = [
        "event_id", "date", "start_time", "end_time", "field",
        "type", "team", "summary", "source", "status", "validation_status",
        "calendar_event_id"
    ]

    sheet.clear()
    sheet.append_row(header)
    sheet.append_rows(updated_rows, value_input_option="USER_ENTERED")
