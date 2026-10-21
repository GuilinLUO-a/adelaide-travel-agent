
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



## API contracts

- [Travel Preferences API](docs/trip-preferences-api.md)
- [Itinerary Generation API](docs/itinerary-api.md)

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
