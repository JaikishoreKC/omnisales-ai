# Architecture

OmniSales AI is a FastAPI backend with a React frontend and a MongoDB datastore. The backend follows a layered structure: transport, orchestration, domain agents, repositories, and external adapters.

## Components

- `app.main`: HTTP routes, middleware, lifespan startup, and error handling.
- `app.orchestrator`: Intent detection, context building, and request routing.
- `app.agents`: Business logic for recommendations, inventory, payments, tracking, and support.
- `app.repositories`: MongoDB access and persistence helpers.
- `app.services`: LLM provider routing (Groq primary, Ollama fallback).
- `app.adapters`: Channel-specific adapters (web, WhatsApp, voice).
- `app.utils`: Serialization, response helpers, parsing, logging context.

## Request flow (chat)

```
Client -> POST /chat
  -> auth + rate limit
  -> save user message
  -> orchestrator routes to agent
  -> LLM provider (Groq or Ollama)
  -> save assistant message
  -> ChatResponse
```

## LLM routing

The LLM service checks providers in order:

1) Groq if `GROQ_API_KEY` is set
2) Ollama if `OLLAMA_URL` or `OLLAMA_API_URL` is set

## Data model

- `User`: account details and preferences
- `Session`: recent messages and cart state
- `Product`: catalog item with optional image/description
- `Order`: order data and status
