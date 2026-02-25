
import os
import sys
import json
import logging
import asyncio
from typing import Any, Sequence

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.stdio import stdio_server
import mcp.types as types

from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configure logging to stderr
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("google-server")

# Define Server
server = Server("google-workspace")

# Constants
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'service_account.json')

def normalize_private_key(key: str) -> str:
    """Ensure private key is in valid PEM format."""
    body = key.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "").replace("\\n", "").replace("\n", "").replace(" ", "")
    chunked = '\n'.join(body[i:i+64] for i in range(0, len(body), 64))
    return f"-----BEGIN PRIVATE KEY-----\n{chunked}\n-----END PRIVATE KEY-----"

def get_credentials():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")
    try:
        with open(SERVICE_ACCOUNT_FILE, 'r') as f:
            info = json.load(f)
        if 'private_key' in info:
            info['private_key'] = normalize_private_key(info['private_key'])
        msg = f"Loaded creds for {info.get('client_email')}"
        logger.info(msg)
        creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
        return creds
    except Exception as e:
        logger.error(f"Error loading credentials: {e}")
        raise

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="list_gmail_messages",
            description="List recent Gmail messages (Subject and Sender).",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_results": {"type": "integer", "default": 5}
                }
            }
        ),
        types.Tool(
            name="list_calendar_events",
            description="List upcoming Google Calendar events.",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_results": {"type": "integer", "default": 5}
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if name == "list_gmail_messages":
        max_results = (arguments or {}).get("max_results", 5)
        try:
            creds = get_credentials()
            service = build('gmail', 'v1', credentials=creds)
            results = service.users().messages().list(userId='me', maxResults=max_results).execute()
            messages = results.get('messages', [])
            
            if not messages:
                return [types.TextContent(type="text", text="No messages found.")]
            
            output = []
            for msg in messages:
                txt = service.users().messages().get(userId='me', id=msg['id']).execute()
                payload = txt['payload']
                headers = payload.get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                output.append(f"- [{sender}]: {subject}")
            
            return [types.TextContent(type="text", text="\n".join(output))]
        except Exception as e:
            logger.exception("Gmail error")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "list_calendar_events":
        max_results = (arguments or {}).get("max_results", 5)
        try:
            creds = get_credentials()
            service = build('calendar', 'v3', credentials=creds)
            events_result = service.events().list(
                calendarId='primary', maxResults=max_results, singleEvents=True, orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            
            if not events:
                return [types.TextContent(type="text", text="No upcoming events found.")]
                
            output = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'No Title')
                output.append(f"- {start}: {summary}")
            
            return [types.TextContent(type="text", text="\n".join(output))]
        except Exception as e:
            logger.exception("Calendar error")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
            
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    # Run the server using stdin/stdout streams
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
