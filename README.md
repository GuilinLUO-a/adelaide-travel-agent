## Current functionality

- React frontend checks the Python backend connection.
- Users can enter destination, dates, total budget in AUD,
  number of travellers, and optional interests.
- React submits preferences to POST /api/trip-preferences.
- FastAPI validates preferences and returns the accepted values.
- The page displays a confirmation summary from the backend response.
- Validation errors and connection failures display useful messages.
- Form controls are disabled while submitting.
- Users can retry after a failed request.

Preferences are validated and displayed but are not saved.
AI itinerary generation will be added in a later module.

## API contract

See [Travel Preferences API](docs/trip-preferences-api.md).

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
