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
    - Removes rows for events no longer in the ICS feed
    """

    sheet_id = os.environ["GOOGLE_SHEET_ID"]
    sheet = get_sheet(sheet_id, "Events")

    # Fetch existing rows (skip header)
    existing = sheet.get_all_values()[1:]

    # Build a set of ICS event_ids
    incoming_ids = {e["event_id"] for e in events}

    # --- RECONCILE: keep only rows whose event_id still exists ---
    updated_rows = [row for row in existing if row[0] in incoming_ids]

    # --- REBUILD INDEX MAP AFTER RECONCILIATION ---
    existing_map = {row[0]: idx for idx, row in enumerate(updated_rows)}

    # --- UPSERT incoming events ---
    for e in events:
        # Local date/time (correct)
        date = e["start"].date().isoformat()
        start_time = e["start"].strftime("%H:%M")
        end_time = e["end"].strftime("%H:%M")

        row = [
            e["event_id"],
            date,
            start_time,
            end_time,
            e.get("field", ""),                 # validator sets this
            e.get("type", "game"),
            e.get("team", ""),
            e.get("summary") or "",             # FIXED: never write None
            "ICS",
            "active",
            e.get("validation_status", "OK"),
            ""
        ]

        if e["event_id"] in existing_map:
            # Update existing row
            idx = existing_map[e["event_id"]]
            updated_rows[idx] = row
        else:
            # Insert new row
            existing_map[e["event_id"]] = len(updated_rows)
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
