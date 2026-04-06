# Can You Book Me?

Public availability calendar for **David** — powered by Google Calendar, Flask, and FullCalendar.js.

Visitors see David's real-time availability without needing to authenticate. Events are pulled from pre-configured Google Calendars and displayed in a responsive, installable web app.

---

## Features

- **Google Calendar sync** — pulls events from one or more calendars via the Google Calendar API v3
- **Multi-calendar color support** — each calendar renders in its own color; individual event colors are respected when set
- **Timezone-aware** — detects the visitor's local timezone; shows the original event timezone when different
- **Responsive** — week view on desktop, day view on tablet, list view on mobile
- **PWA** — installable on Android (native prompt) and iPhone (via share sheet); works offline with service worker cache
- **Private events** — events marked as confidential show as "Busy" without leaking details

---

## Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.11 · Flask 3 |
| Calendar API | Google Calendar API v3 · OAuth2 with PKCE |
| Frontend | FullCalendar.js v6 · Vanilla JS |
| Styling | CSS custom properties · Plus Jakarta Sans |
| PWA | Service Worker · Web App Manifest |
| Package manager | `uv` |

---

## Project structure

```
can-you-book-me/
├── src/
│   ├── main.py                      # Flask app factory
│   ├── .env                         # Local secrets (not committed)
│   ├── .env.template                # Variables reference
│   ├── routes/
│   │   ├── calendar.py              # GET /api/events  (public)
│   │   ├── admin.py                 # GET /admin/setup + /admin/callback (OAuth2 flow)
│   │   ├── stats.py                 # GET /api/stats
│   │   └── health.py
│   ├── services/
│   │   └── gcalendar.py             # Google Calendar service (PKCE OAuth2, event fetching)
│   ├── security/
│   │   ├── auth.py                  # require_api_key decorator
│   │   └── credentials_manager.py  # Loads .env into a dict
│   ├── utils/
│   │   └── logger.py
│   ├── templates/
│   │   └── index.html               # Single-page shell
│   └── static/
│       ├── css/style.css
│       ├── js/app.js                # FullCalendar init, timezone logic, install prompt
│       ├── sw.js                    # Service worker (network-first local, cache-first CDN)
│       ├── manifest.json
│       └── icons/
└── pyproject.toml
```

---

## Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment

```bash
cp src/.env.template src/.env
```

Fill in `src/.env`:

```env
API_KEY=your_secret_api_key
PORT=8080
SECRET_KEY=any_random_string

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://127.0.0.1:8080/admin/callback

# Obtained in step 4
GOOGLE_REFRESH_TOKEN=

# Comma-separated calendar IDs (e.g. "primary" or the calendar's email address)
CALENDAR_IDS=primary
```

### 3. Create a Google Cloud project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project and enable the **Google Calendar API**
3. Create **OAuth 2.0 credentials** → type: *Web application*
4. Add `http://127.0.0.1:8080/admin/callback` to *Authorized redirect URIs*
5. Copy the **Client ID** and **Client Secret** to `.env`

### 4. Obtain the refresh token

Start the app, then visit:

```
http://127.0.0.1:8080/admin/setup?api_key=YOUR_API_KEY
```

Complete the Google consent screen. The refresh token will appear in the server logs and in the JSON response. Copy it to `GOOGLE_REFRESH_TOKEN` in `.env`.

> This step is done once. The refresh token does not expire as long as the app keeps using it.

### 5. Configure calendars

In `.env`, set `CALENDAR_IDS` to a comma-separated list of calendar IDs:

```env
CALENDAR_IDS=primary,your.email@gmail.com,abc123xyz@group.calendar.google.com
```

Calendar IDs can be found in Google Calendar → Settings → each calendar → *Calendar ID*.

### 6. Run

```bash
cd src && uv run python main.py
```

---

## API endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/` | — | Calendar frontend |
| `GET` | `/api/events?start=&end=` | — | Events in FullCalendar format |
| `GET` | `/admin/setup` | `?api_key=` | Starts OAuth2 flow |
| `GET` | `/admin/callback` | — | OAuth2 callback, logs refresh token |
| `GET` | `/api/stats` | — | Basic app stats |

---

## Service worker caching

| Resource | Strategy |
|---|---|
| `/api/*`, `/admin/*` | Network only |
| CDN (FullCalendar) | Cache-first (versioned URLs) |
| HTML, CSS, JS, icons | Network-first, offline fallback |

Deploying a new version is immediately visible to all clients on next refresh.
