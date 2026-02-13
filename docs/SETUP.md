# Setup

This guide covers local development for the backend and frontend in this repo.

## Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB (local or Atlas)
- Optional LLM provider:
  - OpenRouter (cloud) with `OPENROUTER_API_KEY`
  - Ollama (local) with `OLLAMA_URL` or `OLLAMA_API_URL`

## Backend

1) Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

2) Configure environment

```bash
# From backend/
cp .env.example .env
```

Edit `backend/.env` and set at minimum:

- `MONGO_URI`
- `API_SECRET_KEY`
- `SECRET_KEY` (or rely on `API_SECRET_KEY` as a fallback)
- `OPENROUTER_API_KEY` or `OLLAMA_URL`

Generate keys if needed:

```bash
python -c "import secrets; print('API_SECRET_KEY=' + secrets.token_urlsafe(32)); print('SECRET_KEY=' + secrets.token_urlsafe(32))"
```

3) Seed sample data (optional)

```bash
python load_products.py
```

4) Run the API

```bash
uvicorn app.main:app --reload
```

Server: http://localhost:8000
Docs: http://localhost:8000/docs

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

Optional: create [frontend/.env](frontend/.env) with:

```dotenv
VITE_API_BASE_URL=http://localhost:8000
```

## Verify

- Health: `GET /health`
- Chat (web): `POST /chat` with `X-Session-Id` for guests or `X-User-Token` for authenticated users
- Chat (non-web): `POST /chat` with `Authorization: Bearer <API_SECRET_KEY>`

Example:

```bash
curl http://localhost:8000/health
```

```bash
curl -X POST http://localhost:8000/chat \
  -H "X-Session-Id: session_1" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"guest_session_1","session_id":"session_1","message":"Show me laptops"}'
```

## Troubleshooting

- Mongo connection errors: verify `MONGO_URI` and network access.
- OpenRouter errors: check `OPENROUTER_API_KEY` and model access.
- Ollama errors: ensure Ollama is running and `OLLAMA_URL` is reachable.
