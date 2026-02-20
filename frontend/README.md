# Hospital Workflow Frontend

This is a Vite + React (TypeScript) frontend for the Hospital Workflow backend.

Quick start:

1. cd frontend
2. npm install
3. npm run dev

Environment:
- VITE_API_BASE_URL: Base URL for backend API (default: http://127.0.0.1:8000/api/v1)

Notes:
- Login sends form-urlencoded request to `/login/access-token` to obtain JWT.
- Token is stored in localStorage as `access_token`.

