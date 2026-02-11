# API

Base URL: `http://localhost:8000`

## Auth and rate limits

- `/chat` requires `Authorization: Bearer <API_SECRET_KEY>`.
- Rate limits:
  - `/chat`: 20 requests per minute per IP
  - `/webhook/*`: 100 requests per minute per IP

## Response envelope

Most endpoints return:

```json
{
  "success": true,
  "data": {},
  "message": "",
  "error": null
}
```

`/chat` returns `ChatResponse` directly (no envelope):

```json
{
  "reply": "...",
  "agent_used": "recommendation",
  "actions": []
}
```

## Endpoints

### System

- `GET /`
- `GET /health`

### Chat

- `POST /chat`

Request body:

```json
{
  "user_id": "user_1",
  "session_id": "session_1",
  "message": "Show me laptops",
  "channel": "web"
}
```

### Webhooks

- `POST /webhook/whatsapp`
- `GET /webhook/whatsapp` (verification)
- `POST /webhook/superu`

### Products

- `GET /products`
- `GET /products/{product_id}`

### Auth

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/change-password`
- `POST /auth/request-reset`
- `POST /auth/reset-password`

### Orders

- `POST /orders`
- `GET /orders`
- `GET /orders/{order_id}`

### Reviews

- `POST /reviews`
- `GET /reviews/{product_id}`

### Admin

- `GET /admin/orders`
- `POST /admin/products`
- `PATCH /admin/products/{product_id}`
- `DELETE /admin/products/{product_id}`
- `GET /admin/users`
- `GET /admin/users/{user_id}`

### Profile

- `GET /profile/{user_id}`

## OpenAPI

Interactive docs are available at `/docs` and `/redoc`.
