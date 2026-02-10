from app.repositories.session_repository import get_last_messages, get_cart, get_session
from app.repositories.user_repository import get_user


async def build_context(user_id: str, session_id: str, new_message: str) -> str:
    last_messages = await get_last_messages(session_id)
    session = await get_session(session_id)
    summary = session.get("summary", "") if session else ""
    cart_items = await get_cart(session_id)
    user = await get_user(user_id)
    preferences = user.get("preferences", {}) if user else {}
    
    parts = ["You are an AI sales assistant for OmniSales."]
    
    if summary:
        parts.append(f"\n\n=== SUMMARY ===\n{summary}")
    
    if preferences:
        prefs = "\n".join([f"- {k}: {v}" for k, v in preferences.items()])
        parts.append(f"\n\n=== PREFERENCES ===\n{prefs}")
    
    if cart_items:
        cart = "\n".join([f"- {i.get('name', 'Unknown')} x{i.get('quantity', 1)}" for i in cart_items])
        parts.append(f"\n\n=== CART ===\n{cart}")
    
    if last_messages:
        msgs = "\n".join([f"{m['role'].upper()}: {m['text']}" for m in last_messages])
        parts.append(f"\n\n=== RECENT ===\n{msgs}")
    
    parts.append(f"\n\n=== CURRENT ===\nUSER: {new_message}")
    
    return "".join(parts)
