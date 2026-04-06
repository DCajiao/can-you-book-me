import base64
import hashlib
import json
import secrets

import requests as http_requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from utils.logger import get_logger
from security.credentials_manager import CredentialsManager

logger = get_logger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def _generate_pkce_pair() -> tuple[str, str]:
    """Returns (code_verifier, code_challenge) for PKCE OAuth2 flow."""
    code_verifier = secrets.token_urlsafe(96)
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return code_verifier, code_challenge


class GoogleCalendarService:
    def __init__(self):
        self._creds = CredentialsManager.get_credentials()

    def _build_flow(self) -> Flow:
        client_config = {
            "web": {
                "client_id": self._creds["GOOGLE_CLIENT_ID"],
                "client_secret": self._creds["GOOGLE_CLIENT_SECRET"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self._creds["GOOGLE_REDIRECT_URI"]],
            }
        }
        return Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=self._creds["GOOGLE_REDIRECT_URI"],
        )

    def get_auth_url(self) -> str:
        """
        Generates the OAuth2 authorization URL.
        The code_verifier is embedded in the state parameter so it survives
        the external redirect without relying on the Flask session.
        """
        code_verifier, code_challenge = _generate_pkce_pair()
        # Embed code_verifier in state (base64-encoded JSON)
        state_payload = base64.urlsafe_b64encode(
            json.dumps({"cv": code_verifier}).encode()
        ).decode()

        flow = self._build_flow()
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            prompt="consent",
            code_challenge=code_challenge,
            code_challenge_method="S256",
            state=state_payload,
        )
        return auth_url

    def exchange_code(self, code: str, state: str) -> dict:
        """
        Exchanges the authorization code for tokens.
        Recovers code_verifier from the state parameter returned by Google.
        Uses requests directly to avoid library PKCE handling issues.
        """
        state_data = json.loads(base64.urlsafe_b64decode(state).decode())
        code_verifier = state_data["cv"]

        response = http_requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": self._creds["GOOGLE_CLIENT_ID"],
                "client_secret": self._creds["GOOGLE_CLIENT_SECRET"],
                "redirect_uri": self._creds["GOOGLE_REDIRECT_URI"],
                "grant_type": "authorization_code",
                "code_verifier": code_verifier,
            },
        )
        response.raise_for_status()
        return response.json()

    def get_credentials(self) -> Credentials:
        return Credentials(
            token=None,
            refresh_token=self._creds["GOOGLE_REFRESH_TOKEN"],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self._creds["GOOGLE_CLIENT_ID"],
            client_secret=self._creds["GOOGLE_CLIENT_SECRET"],
            scopes=SCOPES,
        )

    def list_events(self, time_min: str, time_max: str) -> list[dict]:
        calendar_ids = [
            cid.strip()
            for cid in self._creds["CALENDAR_IDS"].split(",")
            if cid.strip()
        ]

        credentials = self.get_credentials()
        service = build("calendar", "v3", credentials=credentials)

        events = []
        for calendar_id in calendar_ids:
            try:
                # calendarList returns the user-facing color and name
                cal_meta = service.calendarList().get(calendarId=calendar_id).execute()
                calendar_name = cal_meta.get("summary", calendar_id)
                calendar_color = (
                    cal_meta.get("backgroundColor")
                    or cal_meta.get("foregroundColor")
                    or "#4285F4"
                )

                result = (
                    service.events()
                    .list(
                        calendarId=calendar_id,
                        timeMin=time_min,
                        timeMax=time_max,
                        singleEvents=True,
                        orderBy="startTime",
                    )
                    .execute()
                )

                for item in result.get("items", []):
                    start = item.get("start", {})
                    end = item.get("end", {})

                    start_dt = start.get("dateTime") or start.get("date")
                    end_dt = end.get("dateTime") or end.get("date")
                    event_timezone = start.get("timeZone") or cal_meta.get("timeZone", "UTC")

                    # Private/confidential events have no summary — show as "Busy"
                    summary = item.get("summary")
                    is_busy = not summary
                    title = summary if summary else "Busy"

                    events.append({
                        "id": item["id"],
                        "title": title,
                        "start": start_dt,
                        "end": end_dt,
                        "color": calendar_color,
                        "allDay": "date" in start,
                        "extendedProps": {
                            "calendar_name": calendar_name,
                            "event_timezone": event_timezone,
                            "description": item.get("description", ""),
                            "location": item.get("location", ""),
                            "is_busy": is_busy,
                        },
                    })

            except HttpError as e:
                logger.error("Error fetching events for calendar '%s': %s", calendar_id, e)

        return events
