from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import get_settings
from app.core.database import connect_db, close_db
from app.models.schemas import ChatRequest, ChatResponse

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(title="OmniSales AI", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    from app.orchestrator.router import route_request
    from app.repositories.session_repository import save_message
    
    await save_message(request.session_id, "user", request.message)
    
    result = await route_request(
        user_id=request.user_id,
        session_id=request.session_id,
        message=request.message
    )
    
    await save_message(request.session_id, "assistant", result["reply"])
    
    return ChatResponse(
        reply=result["reply"],
        agent_used=result["agent_used"],
        actions=result.get("actions")
    )
