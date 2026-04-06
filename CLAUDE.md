# CLAUDE.md

## Project overview

Flask + FullCalendar.js app that publicly displays David's Google Calendar availability. Single-page frontend, no user auth — visitors just see pre-configured calendars.

## Running the app

```bash
cd src && uv run python main.py
```

Runs on the port defined in `.env` (`PORT`). Default: `8080`.

## Key files

| File | Purpose |
|---|---|
| `src/main.py` | Flask app factory, route registration |
| `src/routes/calendar.py` | `GET /api/events` — public event feed |
| `src/routes/admin.py` | OAuth2 setup flow (one-time use) |
| `src/services/gcalendar.py` | Google Calendar API client, PKCE OAuth2, event fetching |
| `src/security/credentials_manager.py` | Loads `.env` into a dict; validates required vars |
| `src/templates/index.html` | Single-page HTML shell |
| `src/static/js/app.js` | FullCalendar init, timezone display, PWA install prompt |
| `src/static/css/style.css` | All styles — CSS custom properties, blue theme |
| `src/static/sw.js` | Service worker — network-first local, cache-first CDN |

## Environment variables

All in `src/.env` (copy from `src/.env.template`):

```
API_KEY            # Protects /admin/setup
PORT               # Flask port (default 8080)
SECRET_KEY         # Flask session secret
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
GOOGLE_REFRESH_TOKEN   # Obtained once via /admin/setup
GOOGLE_REDIRECT_URI    # Must match Google Console (e.g. http://127.0.0.1:8080/admin/callback)
CALENDAR_IDS           # Comma-separated calendar IDs
```

## Architecture notes

### OAuth2 / PKCE
The PKCE `code_verifier` is embedded in the OAuth2 `state` parameter (base64-encoded JSON) because Flask session cookies don't survive the external Google redirect reliably. Recovered in `/admin/callback` by decoding state.

### Calendar colors
- Calendar-level color: fetched via `calendarList().get()` (returns `backgroundColor`)
- Event-level color: fetched once via `colors().get()` to build a `colorId → hex` map; event color takes priority over calendar color

### Google Calendar API quirks
- `events.list` requires RFC3339 timestamps — `calendar.py` appends `Z` if no timezone offset is present
- Private/confidential events have no `summary` field — rendered as "Busy" with description/location hidden
- Use `calendarList` (not `calendars`) for user-facing metadata like `backgroundColor`

### Service worker strategy
- `/api/*`, `/admin/*` → network only (never cached)
- CDN assets (FullCalendar from jsDelivr) → cache-first (URLs are version-pinned)
- Everything else → network-first; cache used only as offline fallback
- Bump `CACHE_VERSION` in `sw.js` when deploying breaking changes to force cache invalidation

### PWA install
- Android/Chrome: `beforeinstallprompt` event → native prompt
- iOS Safari: UA detection → show tooltip with manual steps (Share → Add to Home Screen)
- Button hidden when already running in standalone mode

## Frontend conventions

- All styles use CSS custom properties defined in `:root` — edit tokens there first
- FullCalendar slot height is controlled via `.fc .fc-timegrid-slot { height }` in CSS, not via JS props
- Event chips use `--chip-color` CSS variable set inline by `renderEventContent()` in `app.js`
- `loading` callback in FullCalendar drives the loading overlay show/hide

## Adding a new calendar

1. Find the calendar ID in Google Calendar → Settings → *Calendar ID*
2. Add it to `CALENDAR_IDS` in `src/.env` (comma-separated)
3. Ensure the Google account that owns the OAuth credentials has access to that calendar
