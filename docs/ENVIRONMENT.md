# Environment

The backend reads settings from `backend/.env` using Pydantic settings. Copy the template and fill required values.

```bash
cd backend
cp .env.example .env
```

## Variables

| Name | Required | Default | Description |
| --- | --- | --- | --- |
| `MONGO_URI` | yes | none | MongoDB connection string. |
| `DB_NAME` | no | `omnisales` | Database name. |
| `OPENROUTER_API_KEY` | no | empty | OpenRouter API key (primary LLM). |
| `OPENROUTER_MODEL` | no | `openrouter/auto` | OpenRouter model name. |
| `OPENROUTER_BASE_URL` | no | `https://openrouter.ai/api/v1` | OpenRouter base URL. |
| `OLLAMA_API_URL` | no | `http://localhost:11434` | Ollama base URL (fallback LLM). |
| `API_SECRET_KEY` | yes | empty | Bearer token for `/chat`. |
| `SECRET_KEY` | yes | empty | JWT signing key for auth flows. If empty, `API_SECRET_KEY` is used. |
| `FRONTEND_URL` | no | `http://localhost:5173` | Allowed CORS origin. |
| `ENVIRONMENT` | no | `development` | `development` or `production`. |
| `WHATSAPP_API_TOKEN` | no | empty | WhatsApp Business API token. |
| `WHATSAPP_PHONE_ID` | no | empty | WhatsApp phone number ID. |
| `WHATSAPP_VERIFY_TOKEN` | no | empty | Webhook verification token. |
| `SUPERU_API_KEY` | no | empty | SuperU voice API key. |
| `SUPERU_FROM_NUMBER` | no | empty | SuperU outbound number. |
| `SUPERU_WEBHOOK_URL` | no | empty | Public webhook URL for SuperU callbacks. |
| `POS_API_URL` | no | empty | POS integration URL. |
| `POS_API_KEY` | no | empty | POS integration key. |

## Minimal .env example

```dotenv
MONGO_URI=mongodb://localhost:27017
DB_NAME=omnisales
API_SECRET_KEY=replace_me
SECRET_KEY=replace_me
OPENROUTER_API_KEY=replace_me
OPENROUTER_MODEL=openrouter/auto
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
FRONTEND_URL=http://localhost:5173
ENVIRONMENT=development
```
