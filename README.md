
## Current functionality

### Module 1 — Backend connection
- React checks connectivity with the FastAPI backend.
- The user sees connection success and failure messages.

### Module 2 — Travel preferences
- Users enter destination, dates, total budget in AUD,
  number of travellers, and optional interests.
- FastAPI validates travel preferences.
- React displays accepted preferences.
- Invalid inputs and connection errors are handled.

### Module 3 — Itinerary generation
- Users generate itineraries from accepted preferences.
- FastAPI generates day-by-day activity suggestions.
- Interests influence the suggested activities.
- The total budget is allocated across travel days.
- React displays each day and its activities.
- Loading, error handling, and retry are supported.
- Automated backend tests cover generation and API validation.

Itinerary generation currently uses deterministic Python logic,
not a large language model (LLM).

Activity suggestions are illustrative.
Budget allocations are not verified travel prices.

Trips are not saved to a database.

### Module 4 — Places, routes, and maps

- Activities include selected places, addresses, and coordinates.
- Google Places and Google Routes are accessed through backend adapters.
- Mock providers support development and automated tests.
- Source information, retrieval times, and estimates are displayed.
- Missing information and provider failures produce explanatory messages.
- A Google map displays distinct places and available walking-route geometry.
- Loading feedback, duplicate-request protection, and retry are preserved.


## API contracts

- [Travel Preferences API](docs/trip-preferences-api.md)
- [Itinerary Generation API](docs/itinerary-api.md)
- [Travel Data API](docs/travel-data-api.md)

## Local setup — Windows Command Prompt

Run these commands from the repository root.

### Backend — first-time setup

```bat
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

### Backend — start

```bat
cd backend
.venv\Scripts\activate
python -m uvicorn main:app --reload
```

Backend API documentation: http://127.0.0.1:8000/docs

### Frontend — first-time setup

In a separate terminal:

```bat
cd frontend
npm install
```

### Frontend — start

```bat
cd frontend
npm run dev
```

Open the Local URL printed by Vite.
Keep both terminals running. Press Ctrl+C in each terminal to stop it.


## Testing

### Backend

From the repository root:

```bat
cd backend
.venv\Scripts\activate
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

### Frontend

From the repository root:

```bat
cd frontend
npm install
npm run lint
npm run build
```

### Manual verification

1. Start the backend and frontend.
2. Check backend connectivity.
3. Submit valid travel preferences.
4. Generate and display an itinerary.
5. Test a single-day trip and empty interests.
6. Test backend failure and retry.
7. Confirm that changing preferences clears the old itinerary.

## Module 4 configuration

Adelaide is the initial supported destination.

Follow the local setup instructions above to install dependencies.

### Mock backend

In the backend terminal, with the virtual environment active:

```bat
set "PLACE_PROVIDER=mock"
set "ROUTE_PROVIDER=mock"
python -m uvicorn main:app --reload
```

Mock places and route measurements are synthetic development data.
They are labelled in the interface.

### Google-backed places and routes

Enable these services in your Google Cloud project:

- Places API (New)
- Routes API
- Maps JavaScript API

In the backend terminal:

```bat
set "PLACE_PROVIDER=google_places"
set "ROUTE_PROVIDER=google_routes"
set "GOOGLE_PLACES_API_KEY=your_places_key"
set "GOOGLE_ROUTES_API_KEY=your_routes_key"
python -m uvicorn main:app --reload
```

Stop an existing backend server before restarting with different settings.
Command Prompt environment variables apply to that terminal and its child processes.

### Browser map

For a fresh checkout, run from `frontend`:

```bat
copy .env.example .env.local
```

Set `VITE_GOOGLE_MAPS_API_KEY` in `.env.local` to a separate browser key.

Restrict that key to Maps JavaScript API and these development websites:

- `http://localhost:5173/*`
- `http://127.0.0.1:5173/*`

Vite exposes `VITE_` settings to the browser. Backend Places and Routes keys
belong in backend configuration.

Restart Vite after changing `.env.local`.

The map currently uses Google's `DEMO_MAP_ID` for development.
Google map loads use Google Maps Platform services even when the backend
uses mock providers.

### Behaviour and limitations

- Places are selected using deterministic activity categories.
- Opening hours, exact venue suitability, prices, and booking availability
  are not verified.
- Daily budgets are planning allocations.
- Walking distances and durations are estimates.
- Activities remain usable when some place or route information is missing.
- Route lines require returned geometry; mock routes have no geometry.
- The map combines available places and routes across all trip days.
- Retrieval timestamps record when the application fetched the data.
- Trips are not persisted to a database.

Automated backend tests use controlled provider responses and do not
require live Google API keys.