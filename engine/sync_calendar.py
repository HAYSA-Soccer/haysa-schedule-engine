import os
import json
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service():
    creds = Credentials.from_service_account_info(
        json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_KEY"]),
        scopes=SCOPES
    )
    return build("calendar", "v3", credentials=creds)

def sync_events_to_calendar(events, calendar_id):
    """
    Syncs validated events to a specific Google Calendar.
    - Creates new events
    - Updates existing events
    - Deletes removed events
    """
    service = get_calendar_service()

    # Fetch existing events from the calendar
    existing = service.events().list(
        calendarId=calendar_id,
        maxResults=2500,
        singleEvents=True,
        orderBy="startTime"
    ).execute().get("items", [])

    existing_by_id = {e.get("id"): e for e in existing}

    # Track which events remain after syncing
    seen_ids = set()

    for e in events:
        eid = e["event_id"]
        seen_ids.add(eid)

        event_body = {
            "id": eid,
            "summary": e["summary"],
            "location": e["location"],
            "description": e["description"],
            "start": {"dateTime": e["start"].isoformat(), "timeZone": "America/New_York"},
            "end": {"dateTime": e["end"].isoformat(), "timeZone": "America/New_York"},
        }

        if eid in existing_by_id:
            # Update existing event
            service.events().update(
                calendarId=calendar_id,
                eventId=eid,
                body=event_body
            ).execute()
        else:
            # Create new event
            service.events().insert(
                calendarId=calendar_id,
                body=event_body
            ).execute()

    # Delete events that no longer exist
    for eid, ev in existing_by_id.items():
        if eid not in seen_ids:
            service.events().delete(
                calendarId=calendar_id,
                eventId=eid
            ).execute()
