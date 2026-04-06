from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from utils.logger import get_logger
from security.credentials_manager import CredentialsManager

logger = get_logger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


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

    def get_auth_url(self) -> tuple[str, str | None]:
        """Returns (auth_url, code_verifier). Save code_verifier in session."""
        flow = self._build_flow()
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        # requests-oauthlib stores the PKCE verifier on the session object
        code_verifier = getattr(flow.oauth2session, "code_verifier", None)
        return auth_url, code_verifier

    def exchange_code(self, code: str, code_verifier: str | None = None) -> dict:
        flow = self._build_flow()
        flow.fetch_token(code=code, code_verifier=code_verifier)
        token = flow.credentials
        return {
            "access_token": token.token,
            "refresh_token": token.refresh_token,
            "token_uri": token.token_uri,
            "client_id": token.client_id,
            "client_secret": token.client_secret,
        }

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
                cal_meta = service.calendars().get(calendarId=calendar_id).execute()
                calendar_name = cal_meta.get("summary", calendar_id)
                calendar_color = cal_meta.get("backgroundColor", "#4285F4")

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

                    events.append({
                        "id": item["id"],
                        "title": item.get("summary", "(sin título)"),
                        "start": start_dt,
                        "end": end_dt,
                        "color": calendar_color,
                        "allDay": "date" in start,
                        "extendedProps": {
                            "calendar_name": calendar_name,
                            "event_timezone": event_timezone,
                            "description": item.get("description", ""),
                            "location": item.get("location", ""),
                        },
                    })

            except HttpError as e:
                logger.error("Error fetching events for calendar '%s': %s", calendar_id, e)

        return events
