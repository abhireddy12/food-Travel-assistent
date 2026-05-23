# Food & Travel Assistant

A full-stack travel planner that generates day-wise itineraries with famous places and food spots, plus a Gemini-powered chatbot for follow-up trip planning.

## Project Structure

- `backend/` - Flask API with Gemini integration
- `frontend/` - React + css

## Features

- Location validation with Gemini-backed similarity suggestions
- Day-wise itinerary generation with morning, afternoon, and evening slots
- Budget-aware place and food recommendations
- Floating chatbot widget that keeps trip context during the session

## Requirements

- Python 3.10+
- Node.js 18+
- Gemini API key

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Add your Gemini key to `backend/.env`:

```env
GEMINI_API_KEY=your_key_here
```

Run the API:

```bash
flask --app app run --debug
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

If you want the frontend to talk to a backend running elsewhere, set:

```env
VITE_API_BASE_URL=http://127.0.0.1:5000
```

## API Endpoints

- `POST /validate-location`
- `POST /generate-itinerary`
- `POST /chat`

## Notes

The backend includes a demo fallback when `GEMINI_API_KEY` is missing so the UI can still be exercised during development. For production, set the API key and rely on Gemini responses.
