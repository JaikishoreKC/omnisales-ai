from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import get_settings
from app.core.database import connect_db, close_db, get_database
from app.core.gateway import MessageGateway, ChannelType
from app.adapters.web import WebAdapter
from app.adapters.whatsapp import WhatsAppAdapter
from app.adapters.voice import VoiceAdapter
from app.models.schemas import ChatRequest, ChatResponse
from app.models.webhooks import WhatsAppWebhookPayload, SuperUWebhookPayload, ChatRequestValidated
from app.middleware.auth import SecurityHeadersMiddleware, security, verify_api_key

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Initialize message gateway
message_gateway = MessageGateway()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    
    # Create database indexes for performance
    logger.info("Creating database indexes...")
    db = get_database()
    await db.users.create_index("user_id", unique=True)
    await db.sessions.create_index("session_id", unique=True)
    await db.sessions.create_index([("user_id", 1), ("updated_at", -1)])
    await db.products.create_index([("name", "text"), ("category", 1)])
    await db.products.create_index("stock")
    await db.orders.create_index([("user_id", 1), ("created_at", -1)])
    await db.orders.create_index("order_id", unique=True)
    await db.offers.create_index([("active", 1), ("tier_required", 1)])
    logger.info("Database indexes created successfully")
    
    # Register channel adapters
    message_gateway.register_adapter(ChannelType.WEB, WebAdapter())
    message_gateway.register_adapter(ChannelType.WHATSAPP, WhatsAppAdapter())
    message_gateway.register_adapter(ChannelType.VOICE, VoiceAdapter())
    
    yield
    await close_db()


app = FastAPI(
    title="OmniSales AI",
    version="2.0.0",
    description="""
    ## Multi-Agent AI Sales Assistant
    
    OmniSales AI is an intelligent sales assistant platform that helps businesses:
    - **Recommend products** based on customer needs
    - **Check inventory** and stock availability
    - **Process payments** securely
    - **Track orders** in real-time
    - **Manage loyalty programs** and rewards
    - **Handle customer support** queries
    - **Make proactive outbound calls**
    - **Integrate with POS systems**
    
    ### Supported Channels
    - 🌐 **Web Chat** - Direct API integration
    - 💬 **WhatsApp** - WhatsApp Business API
    - 📞 **Voice** - SuperU voice API
    
    ### Authentication
    All endpoints (except webhooks) require Bearer token authentication.
    Use your `API_SECRET_KEY` from the `.env` file.
    
    ### Rate Limiting
    - Chat endpoint: 20 requests/minute
    - Webhook endpoints: 100 requests/minute
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {"name": "root", "description": "API root and navigation"},
        {"name": "system", "description": "System health and status"},
        {"name": "chat", "description": "Chat with AI assistant"},
        {"name": "webhooks", "description": "Integration webhooks for WhatsApp and Voice"},
    ]
)

# Setup rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS configuration - restrict in production
allowed_origins = [settings.frontend_url]
if settings.environment == "development":
    allowed_origins.append("http://localhost:5173")
    allowed_origins.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/", tags=["root"])
async def root():
    """API root endpoint - redirects to documentation"""
    return {
        "message": "Welcome to OmniSales AI",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "chat": "/chat",
            "webhooks": {
                "whatsapp": "/webhook/whatsapp",
                "voice": "/webhook/superu"
            }
        }
    }


@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint - verify API is running"""
    return {"status": "ok", "version": "2.0.0", "channels": ["web", "whatsapp", "voice"]}


@app.post("/chat", response_model=ChatResponse, tags=["chat"])
@limiter.limit("20/minute")
async def chat(
    request: Request,
    chat_request: ChatRequestValidated,
    credentials = Depends(security)
):
    """
    Chat with AI assistant - the main interface for customer interactions
    
    This endpoint intelligently routes your message to one of 8 specialized agents:
    - 💡 **Recommendation Agent** - Product recommendations
    - 📦 **Inventory Agent** - Stock checking
    - 💳 **Payment Agent** - Payment processing
    - 📍 **Order Tracking Agent** - Order status
    - 🎁 **Loyalty Agent** - Rewards & points
    - 🛟 **Support Agent** - Customer service
    - 📞 **Outbound Agent** - Proactive calls
    - 🏪 **POS Integration Agent** - Store systems
    
    ### Authentication Required
    Include your API key in the Authorization header:
    ```
    Authorization: Bearer YOUR_API_SECRET_KEY
    ```
    
    ### Rate Limit
    20 requests per minute per IP address
    
    ### Example Request
    ```json
    {
        "user_id": "customer_123",
        "session_id": "session_456",
        "message": "I need a laptop for coding"
    }
    ```
    """
    from app.orchestrator.router import route_request
    from app.repositories.session_repository import save_message
    
    # Verify API key
    await verify_api_key(credentials, settings)
    
    await save_message(chat_request.session_id, "user", chat_request.message)
    
    result = await route_request(
        user_id=chat_request.user_id,
        session_id=chat_request.session_id,
        message=chat_request.message
    )
    
    await save_message(chat_request.session_id, "assistant", result["reply"])
    
    return ChatResponse(
        reply=result["reply"],
        agent_used=result["agent_used"],
        actions=result.get("actions")
    )


@app.post("/webhook/whatsapp", tags=["webhooks"])
@limiter.limit("100/minute")
async def whatsapp_webhook(request: Request):
    """WhatsApp Business API webhook - receives messages from WhatsApp Business"""
    from app.orchestrator.router import route_request
    from app.repositories.session_repository import save_message
    
    try:
        body = await request.json()
        
        # Validate webhook payload
        try:
            validated_payload = WhatsAppWebhookPayload(**body)
        except Exception as validation_error:
            logger.error(f"WhatsApp webhook validation error: {validation_error}", exc_info=True)
            raise HTTPException(status_code=400, detail="Invalid webhook payload")
        
        # Parse incoming WhatsApp message
        incoming = await message_gateway.receive_message(ChannelType.WHATSAPP, body)
        
        # Save user message
        await save_message(incoming.session_id, "user", incoming.message)
        
        # Route to orchestrator
        result = await route_request(
            user_id=incoming.user_id,
            session_id=incoming.session_id,
            message=incoming.message
        )
        
        # Save assistant reply
        await save_message(incoming.session_id, "assistant", result["reply"])
        
        # Send response via WhatsApp
        from app.core.gateway import OutgoingMessage
        outgoing = OutgoingMessage(
            channel=ChannelType.WHATSAPP,
            user_id=incoming.user_id,
            message=result["reply"],
            actions=result.get("actions")
        )
        
        await message_gateway.send_message(outgoing)
        
        return {"status": "ok"}
    
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/webhook/whatsapp", tags=["webhooks"])
async def whatsapp_webhook_verify(request: Request):
    """WhatsApp webhook verification - required by Meta for webhook setup"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    verify_token = settings.whatsapp_verify_token
    
    if mode == "subscribe" and token == verify_token:
        return int(challenge)
    
    raise HTTPException(status_code=403, detail="Verification failed")


@app.post("/webhook/superu", tags=["webhooks"])
@limiter.limit("100/minute")
async def superu_webhook(request: Request):
    """SuperU voice webhook - receives voice call events from SuperU API"""
    from app.orchestrator.router import route_request
    from app.repositories.session_repository import save_message
    
    try:
        body = await request.json()
        
        # Validate webhook payload
        try:
            validated_payload = SuperUWebhookPayload(**body)
        except Exception as validation_error:
            logger.error(f"SuperU webhook validation error: {validation_error}", exc_info=True)
            raise HTTPException(status_code=400, detail="Invalid webhook payload")
        
        # Parse incoming voice message
        incoming = await message_gateway.receive_message(ChannelType.VOICE, body)
        
        # Save user message
        await save_message(incoming.session_id, "user", incoming.message)
        
        # Route to orchestrator
        result = await route_request(
            user_id=incoming.user_id,
            session_id=incoming.session_id,
            message=incoming.message
        )
        
        # Save assistant reply
        await save_message(incoming.session_id, "assistant", result["reply"])
        
        # Send voice response
        from app.core.gateway import OutgoingMessage
        outgoing = OutgoingMessage(
            channel=ChannelType.VOICE,
            user_id=incoming.user_id,
            message=result["reply"],
            metadata={"call_id": incoming.metadata.get("call_id")}
        )
        
        await message_gateway.send_message(outgoing)
        
        return {"status": "ok"}
    
    except Exception as e:
        logger.error(f"SuperU webhook error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/products", tags=["products"])
@limiter.limit("100/minute")
async def get_products(
    request: Request,
    category: str = None,
    search: str = None,
    limit: int = 20,
    skip: int = 0
):
    """
    Get products list with optional filtering
    
    - **category**: Filter by category (shirts, shoes, jeans, electronics)
    - **search**: Search in product name
    - **limit**: Max products to return (default 20)
    - **skip**: Number of products to skip for pagination
    """
    from app.repositories.product_repository import find_products
    
    query_filter = {}
    
    if category and category != "all":
        query_filter["category"] = category
    
    if search:
        query_filter["name"] = {"$regex": search, "$options": "i"}
    
    # Get total count
    db = get_database()
    total = await db.products.count_documents(query_filter)
    
    # Get products
    cursor = db.products.find(query_filter).skip(skip).limit(limit)
    products = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string
    for product in products:
        product["_id"] = str(product["_id"])
    
    return {
        "products": products,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }


@app.get("/products/{product_id}", tags=["products"])
@limiter.limit("100/minute")
async def get_product_detail(
    request: Request,
    product_id: str
):
    """
    Get detailed information about a specific product
    
    - **product_id**: The unique product identifier
    """
    from app.repositories.product_repository import get_product_by_id
    
    product = await get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Convert ObjectId to string
    product["_id"] = str(product["_id"])
    
    return product
