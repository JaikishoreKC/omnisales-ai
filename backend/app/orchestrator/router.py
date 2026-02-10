from typing import Dict, Any
from app.orchestrator.intent import detect_intent
from app.orchestrator.context import build_context
from app.services.llm_service import generate_response
from app.agents.recommendation import recommend_products
from app.agents.inventory import check_stock
from app.agents.payment import process_payment
from app.agents.fulfillment import track_order
from app.repositories.session_repository import get_cart
from app.utils.parsers import extract_product_name, extract_order_id


async def route_request(user_id: str, session_id: str, message: str) -> Dict[str, Any]:
    intent = detect_intent(message)
    
    agent_result = None
    actions = []
    
    if intent == "recommendation":
        agent_result = await recommend_products(user_id, session_id)
        if agent_result:
            actions.append({"type": "show_products", "data": agent_result})
    
    elif intent == "inventory":
        product_name = extract_product_name(message)
        if product_name:
            agent_result = await check_stock(product_name)
            if agent_result:
                actions.append({"type": "show_stock", "data": agent_result})
    
    elif intent == "payment":
        cart_items = await get_cart(session_id)
        if cart_items:
            agent_result = await process_payment(user_id, cart_items)
            if agent_result and agent_result.get("success"):
                actions.append({"type": "order_created", "data": agent_result})
    
    elif intent == "tracking":
        order_id = extract_order_id(message)
        if order_id:
            agent_result = await track_order(order_id)
            if agent_result:
                actions.append({"type": "order_status", "data": agent_result})
    
    context = await build_context(user_id, session_id, message)
    
    if agent_result:
        context += f"\n\n=== AGENT RESULT ===\n{str(agent_result)}"
    
    llm_reply = await generate_response(context)
    
    return {
        "reply": llm_reply or "I'm sorry, I couldn't process your request.",
        "agent_used": intent,
        "actions": actions if actions else None
    }
