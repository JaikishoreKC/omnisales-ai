# OmniSales AI

OmniSales AI is a multi-channel sales assistant with a FastAPI backend and a React frontend. It supports web, WhatsApp, and voice channels, and routes requests through specialized agents with Groq as the primary LLM provider and Ollama as a fallback.

## Quick start

See [docs/SETUP.md](docs/SETUP.md) for the full walkthrough.

## Documentation

- [docs/SETUP.md](docs/SETUP.md)
- [docs/ENVIRONMENT.md](docs/ENVIRONMENT.md)
- [docs/API.md](docs/API.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/SECURITY.md](docs/SECURITY.md)
- [docs/TESTING.md](docs/TESTING.md)
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)

## Stack

- Backend: FastAPI, Motor (MongoDB), Pydantic, SlowAPI
- Frontend: React, Vite, Tailwind, Zustand
- LLM: Groq (primary), Ollama (fallback)

## API notes

- `/chat` requires `Authorization: Bearer <API_SECRET_KEY>`.
- Most endpoints return a standard envelope; `/chat` returns a direct `ChatResponse`.
- API docs are available at `http://localhost:8000/docs`.

## Repo layout

```
omnisales-ai/
├── backend/
├── frontend/
└── docs/
```
