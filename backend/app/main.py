from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
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
from app.models.schemas import ChatRequest, ChatResponse, ApiResponse
from app.models.webhooks import WhatsAppWebhookPayload, SuperUWebhookPayload, ChatRequestValidated
from app.middleware.auth import SecurityHeadersMiddleware, security, verify_api_key
from app.middleware.request_id import RequestIdMiddleware
from app.utils.serializers import serialize_doc, serialize_list
from app.utils.response import api_success, api_error
from app.utils.logging_context import RequestIdFilter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(request_id)s - %(message)s'
)
logger = logging.getLogger(__name__)

for handler in logging.getLogger().handlers:
    handler.addFilter(RequestIdFilter())

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
app.add_middleware(RequestIdMiddleware)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=api_error(message=exc.detail, error=exc.detail)
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=api_error(message="Validation error", error=str(exc))
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=api_error(message="Internal server error")
    )

# CORS configuration - restrict in production
allowed_origins = [origin.strip() for origin in settings.frontend_url.split(",") if origin.strip()]
if settings.environment == "development":
    allowed_origins.append("http://localhost:5173")
    allowed_origins.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/", tags=["root"], response_model=ApiResponse)
async def root():
    """API root endpoint - redirects to documentation"""
    return api_success({
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
    })


@app.get("/health", tags=["system"], response_model=ApiResponse)
async def health_check():
    """Health check endpoint - verify API is running"""
    db_status = "ok"
    try:
        db = get_database()
        await db.command("ping")
    except Exception:
        db_status = "error"

    return api_success({
        "status": "ok",
        "version": "2.0.0",
        "channels": ["web", "whatsapp", "voice"],
        "database": db_status
    })


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


@app.post("/webhook/whatsapp", tags=["webhooks"], response_model=ApiResponse)
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
        
        return api_success({"status": "ok"})
    
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


@app.post("/webhook/superu", tags=["webhooks"], response_model=ApiResponse)
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
        
        return api_success({"status": "ok"})
    
    except Exception as e:
        logger.error(f"SuperU webhook error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/products", tags=["products"], response_model=ApiResponse)
@limiter.limit("100/minute")
async def get_products(
    request: Request,
    category: str = None,
    search: str = None,
    sort_by: str = "name",
    sort_order: str = "asc",
    stock_filter: str = None,
    limit: int = 20,
    skip: int = 0
):
    """
    Get products list with optional filtering and sorting
    
    - **category**: Filter by category (shirts, shoes, jeans, electronics)
    - **search**: Search in product name
    - **sort_by**: Sort field (name, price, stock, created_at)
    - **sort_order**: Sort direction (asc, desc)
    - **stock_filter**: Filter by stock status (in_stock, low_stock, out_of_stock)
    - **limit**: Max products to return (default 20)
    - **skip**: Number of products to skip for pagination
    """
    from app.repositories.product_repository import find_products
    
    query_filter = {}
    
    if category and category != "all":
        query_filter["category"] = category
    
    if search:
        query_filter["name"] = {"$regex": search, "$options": "i"}
    
    # Stock filtering
    if stock_filter == "out_of_stock":
        query_filter["stock"] = {"$lte": 0}
    elif stock_filter == "low_stock":
        query_filter["stock"] = {"$gt": 0, "$lte": 10}
    elif stock_filter == "in_stock":
        query_filter["stock"] = {"$gt": 10}
    
    # Get total count
    db = get_database()
    total = await db.products.count_documents(query_filter)
    
    # Sort direction
    sort_direction = 1 if sort_order == "asc" else -1
    
    # Get products with sorting
    cursor = db.products.find(query_filter).sort(sort_by, sort_direction).skip(skip).limit(limit)
    products = await cursor.to_list(length=limit)
    
    products = serialize_list(products)
    
    return api_success({
        "products": products,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    })


@app.get("/products/{product_id}", tags=["products"], response_model=ApiResponse)
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
    
    return api_success(serialize_doc(product))


# ==================== Authentication Endpoints ====================

from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@app.post("/auth/register", tags=["auth"], response_model=ApiResponse)
async def register(request: RegisterRequest):
    """Register a new user"""
    from app.auth import get_user_by_email, create_user, create_access_token
    
    existing_user = await get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = await create_user(request.email, request.password, request.name)
    
    user = serialize_doc(user)
    
    token = create_access_token({"user_id": user["user_id"], "email": user["email"]})
    
    return api_success({"user": user, "token": token})


@app.post("/auth/login", tags=["auth"], response_model=ApiResponse)
async def login(request: LoginRequest):
    """Login user"""
    from app.auth import get_user_by_email, verify_password, create_access_token
    
    user = await get_user_by_email(request.email)
    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Remove sensitive data and convert ObjectId
    user.pop("password_hash", None)
    user = serialize_doc(user)
    
    token = create_access_token({"user_id": user["user_id"], "email": user["email"]})
    
    return api_success({"user": user, "token": token})


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@app.post("/auth/change-password", tags=["auth"], response_model=ApiResponse)
async def change_password(request: Request, password_req: ChangePasswordRequest):
    """Change password for logged-in user"""
    from app.auth import change_password
    
    auth_header = request.headers.get("Authorization")
    user = await get_current_user(auth_header)
    
    # Validate new password
    if len(password_req.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")
    
    success = await change_password(
        user["user_id"],
        password_req.old_password,
        password_req.new_password
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    return api_success({"message": "Password changed successfully"})


class RequestResetRequest(BaseModel):
    email: str


@app.post("/auth/request-reset", tags=["auth"], response_model=ApiResponse)
async def request_password_reset(request: RequestResetRequest):
    """Request a password reset token"""
    from app.auth import create_reset_token
    
    token = await create_reset_token(request.email)
    
    # Always return success to prevent email enumeration
    # In production, send email with token here
    if token and settings.environment == "development":
        # TODO: Send email with reset link: /reset-password?token={token}
        return api_success({
            "message": "If the email exists, a reset link has been sent",
            "token": token
        })

    return api_success({"message": "If the email exists, a reset link has been sent"})


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@app.post("/auth/reset-password", tags=["auth"], response_model=ApiResponse)
async def reset_password(request: ResetPasswordRequest):
    """Reset password using a valid reset token"""
    from app.auth import reset_password_with_token
    
    # Validate new password
    if len(request.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    success = await reset_password_with_token(request.token, request.new_password)
    
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    return api_success({"message": "Password reset successfully"})


# ==================== Order Endpoints ====================

from typing import List

class OrderItem(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int

class ShippingAddress(BaseModel):
    fullName: str
    email: str
    phone: str
    address: str
    city: str
    state: str
    zipCode: str
    country: str

class CreateOrderRequest(BaseModel):
    items: List[OrderItem]
    total_amount: float
    shipping_address: ShippingAddress


async def get_current_user(authorization: str = Depends(lambda x: x)):
    """Dependency to get current user from token"""
    from app.auth import decode_token
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return payload


@app.post("/orders", tags=["orders"], response_model=ApiResponse)
async def create_order(
    request: Request,
    order_req: CreateOrderRequest,
    authorization: str = Depends(lambda: None)
):
    """Create a new order"""
    from app.repositories.order_repository import create_order
    
    # Get authorization from headers
    auth_header = request.headers.get("Authorization")
    user = await get_current_user(auth_header)
    
    order_data = {
        **order_req.dict(),
        "user_id": user["user_id"]
    }

    # Validate stock before order creation
    db = get_database()
    for item in order_req.items:
        product = await db.products.find_one({"product_id": item.product_id})
        if not product:
            raise HTTPException(status_code=404, detail=f"Product not found: {item.product_id}")
        if product.get("stock", 0) < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {item.name}"
            )

    order = await create_order(
        user["user_id"],
        [item.dict() for item in order_req.items],
        order_req.total_amount,
        order_req.shipping_address.dict()
    )

    # Update product stock
    for item in order_req.items:
        await db.products.update_one(
            {"product_id": item.product_id},
            {"$inc": {"stock": -item.quantity}}
        )
    
    return api_success(serialize_doc(order))


@app.get("/orders", tags=["orders"], response_model=ApiResponse)
async def get_user_orders(request: Request):
    """Get user's orders"""
    from app.repositories.order_repository import get_user_orders
    
    auth_header = request.headers.get("Authorization")
    user = await get_current_user(auth_header)
    
    orders = await get_user_orders(user["user_id"])
    
    return api_success({"orders": serialize_list(orders)})


@app.get("/orders/{order_id}", tags=["orders"], response_model=ApiResponse)
async def get_order_detail(request: Request, order_id: str):
    """Get order details"""
    from app.repositories.order_repository import get_order_by_id
    from app.auth import get_user_by_id
    
    auth_header = request.headers.get("Authorization")
    user = await get_current_user(auth_header)
    
    order = await get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user owns the order or is admin
    user_doc = await get_user_by_id(user["user_id"])
    is_admin = user_doc and user_doc.get("role") == "admin"
    
    if order["user_id"] != user["user_id"] and not is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return api_success(serialize_doc(order))


# ==================== Review Endpoints ====================

class CreateReviewRequest(BaseModel):
    product_id: str
    rating: int
    comment: str

@app.post("/reviews", tags=["reviews"], response_model=ApiResponse)
async def create_review(request: Request, review_req: CreateReviewRequest):
    """Create a product review"""
    from app.repositories.review_repository import create_review
    
    auth_header = request.headers.get("Authorization")
    user = await get_current_user(auth_header)
    
    if review_req.rating < 1 or review_req.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    review = await create_review(
        review_req.product_id,
        user["user_id"],
        user.get("name", "Anonymous"),
        review_req.rating,
        review_req.comment
    )
    
    return api_success(serialize_doc(review))


@app.get("/reviews/{product_id}", tags=["reviews"], response_model=ApiResponse)
async def get_product_reviews(product_id: str):
    """Get reviews for a product"""
    from app.repositories.review_repository import get_product_reviews, get_review_stats
    
    reviews = await get_product_reviews(product_id)
    stats = await get_review_stats(product_id)
    
    return api_success({
        "reviews": serialize_list(reviews),
        "stats": stats
    })


# ==================== Admin Endpoints ====================

@app.get("/admin/orders", tags=["admin"], response_model=ApiResponse)
async def get_all_orders_admin(
    request: Request,
    skip: int = 0,
    limit: int = 50,
    status: str = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    """Get all orders (admin only) with filtering and sorting"""
    from app.repositories.order_repository import get_all_orders
    
    auth_header = request.headers.get("Authorization")
    user = await get_current_user(auth_header)
    
    # Check if user is admin
    from app.auth import get_user_by_id
    user_doc = await get_user_by_id(user["user_id"])
    if not user_doc or user_doc.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Build query filter
    query_filter = {}
    if status and status != "all":
        query_filter["status"] = status
    
    # Get total count
    db = get_database()
    total = await db.orders.count_documents(query_filter)
    
    # Sort direction
    sort_direction = 1 if sort_order == "asc" else -1
    
    # Get orders with filtering and sorting
    cursor = db.orders.find(query_filter).sort(sort_by, sort_direction).skip(skip).limit(limit)
    orders = await cursor.to_list(length=limit)
    
    return api_success({"orders": serialize_list(orders), "total": total})


class CreateProductRequest(BaseModel):
    name: str
    category: str
    price: float
    stock: int

@app.post("/admin/products", tags=["admin"], response_model=ApiResponse)
async def create_product_admin(request: Request, product_req: CreateProductRequest):
    """Create a new product (admin only)"""
    from uuid import uuid4
    
    auth_header = request.headers.get("Authorization")
    user = await get_current_user(auth_header)
    
    from app.auth import get_user_by_id
    user_doc = await get_user_by_id(user["user_id"])
    if not user_doc or user_doc.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_database()
    product = {
        "product_id": str(uuid4()),
        **product_req.dict()
    }
    result = await db.products.insert_one(product)
    product["_id"] = result.inserted_id

    return api_success(serialize_doc(product))


@app.delete("/admin/products/{product_id}", tags=["admin"], response_model=ApiResponse)
async def delete_product_admin(request: Request, product_id: str):
    """Delete a product (admin only)"""
    auth_header = request.headers.get("Authorization")
    user = await get_current_user(auth_header)
    
    from app.auth import get_user_by_id
    user_doc = await get_user_by_id(user["user_id"])
    if not user_doc or user_doc.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_database()
    result = await db.products.delete_one({"product_id": product_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return api_success({"message": "Product deleted"})


class UpdateProductRequest(BaseModel):
    stock: int | None = None
    price: float | None = None

@app.patch("/admin/products/{product_id}", tags=["admin"], response_model=ApiResponse)
async def update_product_admin(request: Request, product_id: str, update_req: UpdateProductRequest):
    """Update product (admin only)"""
    auth_header = request.headers.get("Authorization")
    user = await get_current_user(auth_header)
    
    from app.auth import get_user_by_id
    user_doc = await get_user_by_id(user["user_id"])
    if not user_doc or user_doc.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_database()
    update_data = {k: v for k, v in update_req.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")
    
    result = await db.products.update_one(
        {"product_id": product_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return api_success({"message": "Product updated"})


@app.get("/admin/users", tags=["admin"], response_model=ApiResponse)
async def get_all_users_admin(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    role: str = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    """Get all users (admin only) with filtering and sorting"""
    from app.auth import get_user_by_id, get_all_users
    
    auth_header = request.headers.get("Authorization")
    user = await get_current_user(auth_header)
    
    user_doc = await get_user_by_id(user["user_id"])
    if not user_doc or user_doc.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Build query filter
    query_filter = {}
    if role and role != "all":
        query_filter["role"] = role
    
    # Get total count
    db = get_database()
    total = await db.users.count_documents(query_filter)
    
    # Sort direction
    sort_direction = 1 if sort_order == "asc" else -1
    
    # Get users with filtering and sorting
    cursor = db.users.find(query_filter).sort(sort_by, sort_direction).skip(skip).limit(limit)
    users = await cursor.to_list(length=limit)
    
    return api_success({"users": serialize_list(users), "total": total})


@app.get("/admin/users/{user_id}", tags=["admin"], response_model=ApiResponse)
async def get_user_details_admin(request: Request, user_id: str):
    """Get user details with orders (admin only)"""
    from app.auth import get_user_by_id
    from app.repositories.order_repository import get_user_orders
    
    auth_header = request.headers.get("Authorization")
    user = await get_current_user(auth_header)
    
    user_doc = await get_user_by_id(user["user_id"])
    if not user_doc or user_doc.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get target user
    target_user = await get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove sensitive data
    target_user.pop("password_hash", None)
    target_user = serialize_doc(target_user)
    
    # Get user's orders
    orders = await get_user_orders(user_id, limit=100)
    
    orders = serialize_list(orders)
    
    # Separate current and past orders
    current_orders = [o for o in orders if o.get("status") not in ["delivered", "cancelled"]]
    past_orders = [o for o in orders if o.get("status") in ["delivered", "cancelled"]]
    
    return api_success({
        "user": target_user,
        "current_orders": current_orders,
        "past_orders": past_orders,
        "total_orders": len(orders)
    })


@app.get("/profile/{user_id}", tags=["profile"])
async def get_user_profile(request: Request, user_id: str):
    """Get user profile with orders (own profile or admin)"""
    from app.auth import get_user_by_id
    from app.repositories.order_repository import get_user_orders
    
    auth_header = request.headers.get("Authorization")
    current_user = await get_current_user(auth_header)
    
    # Check if user is viewing own profile or is admin
    current_user_doc = await get_user_by_id(current_user["user_id"])
    is_admin = current_user_doc and current_user_doc.get("role") == "admin"
    
    if current_user["user_id"] != user_id and not is_admin:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get target user
    target_user = await get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove sensitive data
    target_user.pop("password_hash", None)
    target_user = serialize_doc(target_user)
    
    # Get user's orders
    orders = await get_user_orders(user_id, limit=100)
    
    orders = serialize_list(orders)
    
    # Separate current and past orders
    current_orders = [o for o in orders if o.get("status") not in ["delivered", "cancelled"]]
    past_orders = [o for o in orders if o.get("status") in ["delivered", "cancelled"]]
    
    return api_success({
        "user": target_user,
        "current_orders": current_orders,
        "past_orders": past_orders,
        "total_orders": len(orders)
    })
