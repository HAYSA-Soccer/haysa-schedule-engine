import json
import os

SERVICE_ACCOUNT_INFO = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_KEY"])

import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet(sheet_id: str):
    """
    Returns a gspread worksheet object for the first sheet in the spreadsheet.
    """
    creds = Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=SCOPES
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(sheet_id)
    return spreadsheet.sheet1

def write_events_to_sheet(sheet, events):
    """
    Writes parsed ICS events into the Google Sheet.
    Clears old data and writes fresh rows.
    """
    # Clear existing rows (except header)
    sheet.resize(rows=1)

    rows = []
    for e in events:
        rows.append([
            e["event_id"],
            e["start"].isoformat(),
            e["end"].isoformat(),
            e["summary"],
            e["location"],
            e["description"]
        ])

    if rows:
        sheet.append_rows(rows, value_input_option="USER_ENTERED")
