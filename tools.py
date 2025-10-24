"""
Custom tools for the personal assistant agent.
Provides email and calendar operations using Google APIs.
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle


# Google API Scopes
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_google_credentials(scopes: List[str], token_file: str = 'token.pickle') -> Credentials:
    """
    Get or refresh Google API credentials.

    Args:
        scopes: List of OAuth scopes needed
        token_file: Path to token file

    Returns:
        Credentials object
    """
    creds = None

    # Load existing credentials if available
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    # Refresh or create new credentials if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError(
                    "credentials.json not found. Please download it from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
            creds = flow.run_local_server(port=0)

        # Save credentials for future use
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    return creds


async def read_emails(max_results: int = 10, query: str = '') -> Dict[str, Any]:
    """
    Read emails from Gmail.

    Args:
        max_results: Maximum number of emails to retrieve
        query: Gmail search query (e.g., 'is:unread', 'from:example@email.com')

    Returns:
        Dictionary containing email data
    """
    try:
        creds = get_google_credentials(GMAIL_SCOPES, 'gmail_token.pickle')
        service = build('gmail', 'v1', credentials=creds)

        # Get list of messages
        results = service.users().messages().list(
            userId='me',
            maxResults=max_results,
            q=query
        ).execute()

        messages = results.get('messages', [])

        if not messages:
            return {"status": "success", "count": 0, "emails": []}

        emails = []
        for msg in messages:
            # Get full message details
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()

            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')

            emails.append({
                'id': message['id'],
                'subject': subject,
                'from': sender,
                'date': date,
                'snippet': message.get('snippet', '')
            })

        return {"status": "success", "count": len(emails), "emails": emails}

    except Exception as e:
        return {"status": "error", "message": str(e)}


async def list_calendar_events(
    max_results: int = 10,
    time_min: Optional[datetime] = None,
    time_max: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    List upcoming calendar events.

    Args:
        max_results: Maximum number of events to retrieve
        time_min: Start time for events (defaults to now)
        time_max: End time for events (defaults to 7 days from now)

    Returns:
        Dictionary containing calendar events
    """
    try:
        creds = get_google_credentials(CALENDAR_SCOPES, 'calendar_token.pickle')
        service = build('calendar', 'v3', credentials=creds)

        if time_min is None:
            time_min = datetime.utcnow()
        if time_max is None:
            time_max = time_min + timedelta(days=7)

        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min.isoformat() + 'Z',
            timeMax=time_max.isoformat() + 'Z',
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            formatted_events.append({
                'id': event['id'],
                'summary': event.get('summary', 'No Title'),
                'start': start,
                'end': end,
                'location': event.get('location', ''),
                'description': event.get('description', '')
            })

        return {"status": "success", "count": len(formatted_events), "events": formatted_events}

    except Exception as e:
        return {"status": "error", "message": str(e)}


async def create_calendar_event(
    summary: str,
    start_time: str,
    end_time: str,
    description: str = '',
    location: str = '',
    attendees: List[str] = None
) -> Dict[str, Any]:
    """
    Create a new calendar event.

    Args:
        summary: Event title
        start_time: Start time in ISO format (e.g., '2025-10-24T10:00:00')
        end_time: End time in ISO format
        description: Event description
        location: Event location
        attendees: List of attendee email addresses

    Returns:
        Dictionary with creation status
    """
    try:
        creds = get_google_credentials(CALENDAR_SCOPES, 'calendar_token.pickle')
        service = build('calendar', 'v3', credentials=creds)

        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC',
            },
        }

        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]

        created_event = service.events().insert(calendarId='primary', body=event).execute()

        return {
            "status": "success",
            "event_id": created_event['id'],
            "event_link": created_event.get('htmlLink', '')
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


async def search_web(query: str) -> Dict[str, Any]:
    """
    Search the web for information.
    Note: This is a placeholder. The Claude Agent SDK has built-in web search.

    Args:
        query: Search query

    Returns:
        Dictionary with search results
    """
    return {
        "status": "info",
        "message": "Web search is handled by the Claude Agent SDK's built-in capabilities"
    }


# Tool definitions for Claude Agent SDK
TOOLS = [
    {
        "name": "read_emails",
        "description": "Read emails from Gmail. Can filter by query (e.g., 'is:unread', 'from:someone@example.com')",
        "input_schema": {
            "type": "object",
            "properties": {
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of emails to retrieve (default: 10)",
                    "default": 10
                },
                "query": {
                    "type": "string",
                    "description": "Gmail search query for filtering emails",
                    "default": ""
                }
            }
        },
        "function": read_emails
    },
    {
        "name": "list_calendar_events",
        "description": "List upcoming calendar events from Google Calendar",
        "input_schema": {
            "type": "object",
            "properties": {
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of events to retrieve (default: 10)",
                    "default": 10
                }
            }
        },
        "function": list_calendar_events
    },
    {
        "name": "create_calendar_event",
        "description": "Create a new event in Google Calendar",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "Event title"
                },
                "start_time": {
                    "type": "string",
                    "description": "Start time in ISO format (e.g., '2025-10-24T10:00:00Z')"
                },
                "end_time": {
                    "type": "string",
                    "description": "End time in ISO format"
                },
                "description": {
                    "type": "string",
                    "description": "Event description",
                    "default": ""
                },
                "location": {
                    "type": "string",
                    "description": "Event location",
                    "default": ""
                },
                "attendees": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of attendee email addresses",
                    "default": []
                }
            },
            "required": ["summary", "start_time", "end_time"]
        },
        "function": create_calendar_event
    }
]
