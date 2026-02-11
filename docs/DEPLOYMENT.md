# Deployment

This is a minimal deployment guide for the backend. Adjust for your hosting environment.

## Environment

- Set all required variables from [docs/ENVIRONMENT.md](ENVIRONMENT.md).
- Use `ENVIRONMENT=production`.
- Configure `FRONTEND_URL` to your deployed frontend origin.

## Run the API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Reverse proxy

- Terminate TLS at a proxy (nginx, Caddy, or your platform).
- Forward `X-Forwarded-For` and `X-Forwarded-Proto`.

## Observability

- Monitor logs for `request_id` fields.
- Track rate limit responses (`429`) to tune thresholds.
