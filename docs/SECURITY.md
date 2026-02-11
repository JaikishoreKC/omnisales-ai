# Security

## Authentication

- `/chat` requires a Bearer token using `API_SECRET_KEY`.
- Auth endpoints issue JWTs signed with `SECRET_KEY`.

## Rate limiting

- `/chat`: 20 requests per minute per IP
- `/webhook/*`: 100 requests per minute per IP

## Input validation

- Pydantic models validate request shape and constraints.
- Chat input sanitizes message content and validates IDs.

## Security headers

Responses include:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'; ...`

## CORS

- Allowed origins are restricted to `FRONTEND_URL` plus localhost in development.

## Logging

- Requests are tagged with a request ID for traceability.
- Server errors return generic messages to clients.

## Production notes

- Set `ENVIRONMENT=production`.
- Use HTTPS and a reverse proxy.
- Store secrets outside the repo and rotate keys regularly.
