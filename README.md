## Current functionality

- React frontend checks the Python backend connection.
- Failed requests display a useful error.
- The connection can be checked again after restarting the backend.

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
