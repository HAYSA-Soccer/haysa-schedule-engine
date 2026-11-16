import json
import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz

SERVICE_ACCOUNT_INFO = json.loads(
    os.environ["GOOGLE_SERVICE_ACCOUNT_KEY"]
)

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


# -----------------------------
# CLASSIFICATION LOGIC
# -----------------------------
def classify_event(e):

    summary = (
        e.get("summary") or ""
    ).lower().strip()

    # Games
    if "vs" in summary:
        return "game"

    # Practices
    if "practice" in summary:
        return "practice"

    # Default
    return "practice"


# -----------------------------
# WRITE LAST UPDATED TIMESTAMP
# -----------------------------
def update_last_updated_timestamp(sheet_id):

    creds = Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=SCOPES
    )

    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(sheet_id)

    try:
        system_sheet = spreadsheet.worksheet(
            "System"
        )

    except gspread.exceptions.WorksheetNotFound:

        system_sheet = spreadsheet.add_worksheet(
            title="System",
            rows=10,
            cols=2
        )

        system_sheet.update_acell(
            "A1",
            "last_ics_update"
        )

    eastern = pytz.timezone(
        "America/New_York"
    )

    now = datetime.now(
        eastern
    ).strftime(
        "%Y-%m-%d %I:%M %p"
    )

    system_sheet.update_acell(
        "B1",
        now
    )


# -----------------------------
# MAIN UPSERT LOGIC
# -----------------------------
def upsert_events_to_sheet(
    events,
    sheet_id=None
):
    """
    UPSERT events into the Events tab.

    Backward compatible:

        upsert_events_to_sheet(events)

    still writes to GOOGLE_SHEET_ID.

    New usage:

        upsert_events_to_sheet(
            events,
            another_sheet_id
        )
    """

    if sheet_id is None:
        sheet_id = os.environ[
            "GOOGLE_SHEET_ID"
        ]

    sheet = get_sheet(
        sheet_id,
        "Events"
    )

    # Fetch existing rows
    existing = sheet.get_all_values()[1:]

    incoming_ids = {
        e["event_id"]
        for e in events
    }

    updated_rows = [
        row
        for row in existing
        if row[0] in incoming_ids
    ]

    existing_map = {
        row[0]: idx
        for idx, row in enumerate(updated_rows)
    }

    # -----------------------------
    # UPSERT EVENTS
    # -----------------------------
    for e in events:

        date = (
            e["start"]
            .date()
            .isoformat()
        )

        start_time = (
            e["start"]
            .strftime("%H:%M")
        )

        end_time = (
            e["end"]
            .strftime("%H:%M")
        )

        row = [
            e["event_id"],
            date,
            start_time,
            end_time,
            e.get("field", ""),
            e.get("field_display", ""),
            e.get("field_group", ""),
            classify_event(e),
            e.get("team", ""),
            e.get("summary") or "",
            "ICS",
            "active",
            e.get(
                "validation_status",
                "OK"
            ),
            ""
        ]

        if e["event_id"] in existing_map:

            idx = existing_map[
                e["event_id"]
            ]

            updated_rows[idx] = row

        else:

            existing_map[
                e["event_id"]
            ] = len(updated_rows)

            updated_rows.append(row)

    header = [
        "event_id",
        "date",
        "start_time",
        "end_time",
        "field",
        "field_display",
        "field_group",
        "type",
        "team",
        "summary",
        "source",
        "status",
        "validation_status",
        "calendar_event_id"
    ]

    sheet.clear()

    sheet.append_row(header)

    sheet.append_rows(
        updated_rows,
        value_input_option="USER_ENTERED"
    )

    update_last_updated_timestamp(
        sheet_id
    )

def upsert_ts_games_to_sheet(
    events,
    sheet_id=None
):

    if sheet_id is None:
        sheet_id = os.environ[
            "GOOGLE_SHEET_ID"
        ]

    creds = Credentials.from_service_account_info(
        SERVICE_ACCOUNT_INFO,
        scopes=SCOPES
    )

    client = gspread.authorize(
        creds
    )

    spreadsheet = client.open_by_key(
        sheet_id
    )

    try:

        sheet = spreadsheet.worksheet(
            "TS_Games"
        )

    except gspread.exceptions.WorksheetNotFound:

        sheet = spreadsheet.add_worksheet(
            title="TS_Games",
            rows=5000,
            cols=20
        )

    rows = []

    for e in events:

        summary = (
            e.get("summary")
            or ""
        ).strip()

        # ONLY GAME RECORDS
        if (
            " vs. " not in summary
            and
            " vs " not in summary
        ):
            continue

        if " vs. " in summary:

            left, right = summary.split(
                " vs. ",
                1
            )

        else:

            left, right = summary.split(
                " vs ",
                1
            )

        team = ""
        opponent = ""
        home_away = ""

        # Home game
        if "Travel" in left:

            team = left.strip()
            opponent = right.strip()
            home_away = "HOME"

        # Away game
        else:

            team = right.strip()
            opponent = left.strip()
            home_away = "AWAY"

        rows.append([

            e.get(
                "event_id",
                ""
            ),

            e["start"]
                .date()
                .isoformat(),

            e["start"]
                .strftime("%H:%M"),

            e["end"]
                .strftime("%H:%M"),

            team,

            opponent,

            home_away,

            summary,

            e.get(
                "location",
                ""
            ),

            "ICS"

        ])

    header = [

        "event_id",
        "date",
        "start_time",
        "end_time",
        "team",
        "opponent",
        "home_away",
        "summary",
        "location",
        "source"
    
    ]
    
    rows.sort(
        key=lambda r: (
            r[1],  # date
            r[2],  # start_time
            r[4]   # team
        )
    )
    
    sheet.clear()
    
    sheet.append_row(
        header
    )


    if rows:

        sheet.append_rows(
            rows,
            value_input_option="USER_ENTERED"
        )


# -----------------------------
# LOAD FIELD MAPPING
# -----------------------------
def load_field_mapping():
    """
    Loads FieldMapping sheet into a Python dict.
    """

    sheet_id = os.environ[
        "GOOGLE_SHEET_ID"
    ]

    sheet = get_sheet(
        sheet_id,
        "FieldMapping"
    )

    values = sheet.get_all_values()

    headers = values[0]
    rows = values[1:]

    idx = {
        h: i
        for i, h in enumerate(headers)
    }

    mapping = {}

    for r in rows:

        abbr = r[
            idx["abbreviation"]
        ].strip()

        if not abbr:
            continue

        mapping[abbr] = {
            "canonical_field":
                r[idx["canonical_field"]].strip(),

            "surface":
                r[idx["surface"]].strip(),

            "ics_match":
                r[idx["ics_match"]].strip(),

            "practiceAllowed":
                r[idx["practiceAllowed"]]
                .strip()
                .lower() == "yes",

            "gameAllowed":
                r[idx["gameAllowed"]]
                .strip()
                .lower() == "yes",

            "enabled":
                r[idx["enabled"]]
                .strip()
                .lower() == "yes",
        }

    return mapping
