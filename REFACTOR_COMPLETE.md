"""
OMNISALES AI - CLEAN ARCHITECTURE
==================================

FINAL FOLDER STRUCTURE:

backend/app/
├── main.py                      # ONLY routing/bootstrap
├── config.py                    # Settings
├── core/
│   └── database.py              # DB connection layer
├── models/
│   └── schemas.py               # Pydantic models
├── repositories/                # DB access layer (Repository pattern)
│   ├── user_repository.py
│   ├── session_repository.py
│   ├── product_repository.py
│   └── order_repository.py
├── services/                    # External APIs
│   └── llm_service.py           # Async OpenRouter API
├── agents/                      # Business logic (Single responsibility)
│   ├── recommendation.py
│   ├── inventory.py
│   ├── payment.py
│   └── fulfillment.py
├── orchestrator/                # Flow control
│   ├── intent.py                # Intent detection
│   ├── context.py               # Context building
│   └── router.py                # Request routing
└── utils/
    └── parsers.py               # Text extraction utilities

REFACTORED:
- Async/await throughout
- Repository pattern for DB access
- Single responsibility agents
- Bounded message storage (MAX 5)
- Extracted business logic from routes
- Removed duplicate services/models
- Standardized naming

REMOVED REDUNDANT:
- services/openrouter.py (duplicate)
- memory/conversation_memory.py (unused)
- models/conversation.py (unused)
- models/user.py (unused)
- db/mongo.py (replaced by core/database.py)

FIXED LOGIC:
- LLM service now async (httpx)
- Session messages limited to 5
- Cart properly retrieved in payment flow
- Product/order parsing extracted to utils
- Config cleaned (removed duplicate db_name/database_name)
"""
