from typing import Dict, Any
from app.orchestrator.intent import detect_intent
from app.orchestrator.context import build_context
from app.services.llm_service import generate_response
from app.agents.recommendation import recommend_products
from app.agents.inventory import check_stock
from app.agents.payment import process_payment
from app.agents.fulfillment import track_order
from app.agents.loyalty import get_loyalty_points, check_offers, redeem_points
from app.agents.post_purchase import initiate_return, request_refund, report_issue
from app.agents.proactive_call import schedule_follow_up_call, initiate_abandoned_cart_call
from app.agents.pos_adapter import sync_inventory_to_pos, get_pos_inventory
from app.repositories.session_repository import get_cart, update_cart
from app.repositories.product_repository import find_products
from app.utils.parsers import extract_product_name, extract_order_id
import re


def extract_category(message: str) -> str:
    """Extract product category from message"""
    message_lower = message.lower()
    categories = ["shirts", "jeans", "shoes", "electronics", "accessories"]
    for category in categories:
        if category in message_lower or category[:-1] in message_lower:  # Check singular too
            return category
    return None


async def route_request(user_id: str, session_id: str, message: str) -> Dict[str, Any]:
    intent = detect_intent(message)
    
    agent_result = None
    actions = []
    
    if intent == "recommendation":
        agent_result = await recommend_products(user_id, session_id, message)
        if agent_result:
            actions.append({"type": "show_products", "data": agent_result})
    
    elif intent == "inventory":
        category = extract_category(message)
        product_name = extract_product_name(message)
        
        if category:
            # Category query - list products in that category
            products = await find_products({"category": category}, limit=10)
            if products:
                agent_result = [
                    {
                        "name": p.get("name"),
                        "price": p.get("price"),
                        "category": p.get("category"),
                        "stock": p.get("stock", 0)
                    }
                    for p in products
                ]
                actions.append({"type": "show_products", "data": agent_result})
        elif product_name:
            # Specific product query
            agent_result = await check_stock(product_name)
            if agent_result:
                actions.append({"type": "show_stock", "data": agent_result})
        else:
            # General inventory query - show some products
            products = await find_products({}, limit=10)
            if products:
                agent_result = [
                    {
                        "name": p.get("name"),
                        "price": p.get("price"),
                        "category": p.get("category")
                    }
                    for p in products
                ]
                actions.append({"type": "show_products", "data": agent_result})
    
    elif intent == "cart":
        # Cart management
        if "view" in message.lower() or "show" in message.lower() or "my cart" in message.lower():
            # View cart
            cart_items = await get_cart(session_id)
            if cart_items:
                agent_result = {
                    "items": cart_items,
                    "total": sum(item.get("price", 0) * item.get("quantity", 1) for item in cart_items)
                }
                actions.append({"type": "show_cart", "data": agent_result})
            else:
                agent_result = {"items": [], "total": 0}
                actions.append({"type": "show_cart", "data": agent_result})
        
        elif "remove" in message.lower() or "delete" in message.lower():
            # Remove item from cart (simplified - removes all instances)
            product_name = extract_product_name(message)
            cart_items = await get_cart(session_id)
            updated_cart = [item for item in cart_items if product_name.lower() not in item.get("name", "").lower()]
            await update_cart(session_id, updated_cart)
            agent_result = {"success": True, "action": "removed", "cart_size": len(updated_cart)}
            actions.append({"type": "cart_updated", "data": agent_result})
        
        elif "clear" in message.lower() or "empty" in message.lower():
            # Clear entire cart
            await update_cart(session_id, [])
            agent_result = {"success": True, "action": "cleared", "cart_size": 0, "total": 0}
            actions.append({"type": "cart_updated", "data": agent_result})
        
        else:
            # Add to cart
            product_name = extract_product_name(message)
            if product_name:
                from app.repositories.product_repository import find_product_by_name
                product = await find_product_by_name(product_name)
                if product:
                    cart_items = await get_cart(session_id)
                    # Check if product already in cart
                    existing = next((item for item in cart_items if item.get("product_id") == product.get("product_id")), None)
                    if existing:
                        existing["quantity"] = existing.get("quantity", 1) + 1
                    else:
                        cart_items.append({
                            "product_id": product.get("product_id"),
                            "name": product.get("name"),
                            "price": product.get("price"),
                            "quantity": 1
                        })
                    await update_cart(session_id, cart_items)
                    agent_result = {
                        "success": True,
                        "product": product.get("name"),
                        "cart_size": len(cart_items),
                        "total": sum(item.get("price", 0) * item.get("quantity", 1) for item in cart_items)
                    }
                    actions.append({"type": "cart_updated", "data": agent_result})
                else:
                    agent_result = {"success": False, "error": "Product not found"}
    
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
    
    elif intent == "loyalty":
        if "points" in message.lower() or "balance" in message.lower():
            agent_result = await get_loyalty_points(user_id)
        elif "offer" in message.lower() or "deal" in message.lower():
            agent_result = await check_offers(user_id)
        elif "redeem" in message.lower():
            # Simple parsing - in production use NER
            try:
                points_to_redeem = int(''.join(filter(str.isdigit, message)))
                agent_result = await redeem_points(user_id, points_to_redeem)
            except:
                agent_result = await get_loyalty_points(user_id)
        
        if agent_result:
            actions.append({"type": "loyalty_info", "data": agent_result})
    
    elif intent == "post_purchase":
        order_id = extract_order_id(message)
        if order_id:
            if "return" in message.lower():
                agent_result = await initiate_return(order_id, message)
            elif "refund" in message.lower():
                agent_result = await request_refund(order_id)
            elif "issue" in message.lower() or "problem" in message.lower():
                agent_result = await report_issue(order_id, "general", message)
            
            if agent_result:
                actions.append({"type": "support_ticket", "data": agent_result})
    
    elif intent == "proactive":
        if "call me" in message.lower():
            agent_result = await schedule_follow_up_call(user_id, message)
            if agent_result:
                actions.append({"type": "call_scheduled", "data": agent_result})
    
    elif intent == "pos_sync":
        product_name = extract_product_name(message)
        if "inventory" in message.lower() or "stock" in message.lower():
            agent_result = await get_pos_inventory()
        if agent_result:
            actions.append({"type": "pos_sync", "data": agent_result})
    
    context = await build_context(user_id, session_id, message)
    
    # Format agent results for AI context based on type
    if agent_result:
        if isinstance(agent_result, list):
            # Format product list nicely
            if agent_result and isinstance(agent_result[0], dict) and "name" in agent_result[0]:
                products_text = "\n".join([
                    f"- {p.get('name', 'Unknown')} (${p.get('price', 0):.2f}) - Stock: {p.get('stock', 'N/A')}"
                    for p in agent_result
                ])
                context += f"\n\n=== AVAILABLE PRODUCTS ===\n{products_text}\n\nDescribe these products to the customer naturally."
            else:
                context += f"\n\n=== AGENT RESULT ===\n{str(agent_result)}"
        elif isinstance(agent_result, dict):
            # Format dict results based on content
            if "order_id" in agent_result and "status" in agent_result:
                # Order/tracking result
                context += f"\n\n=== ORDER INFORMATION ===\n"
                context += f"Order ID: {agent_result.get('order_id', 'N/A')}\n"
                context += f"Status: {agent_result.get('status', 'unknown')}\n"
                if agent_result.get('total_price'):
                    context += f"Total: ${agent_result.get('total_price', 0):.2f}\n"
                if agent_result.get('eta'):
                    context += f"ETA: {agent_result.get('eta', 'N/A')}\n"
                context += "\nExplain this order status to the customer in a friendly way."
            
            elif "points" in agent_result or "tier" in agent_result:
                # Loyalty result
                context += f"\n\n=== LOYALTY INFORMATION ===\n"
                context += f"Points Balance: {agent_result.get('points', 0)}\n"
                context += f"Tier: {agent_result.get('tier', 'bronze').title()}\n"
                if agent_result.get('lifetime_value'):
                    context += f"Lifetime Value: ${agent_result.get('lifetime_value', 0):.2f}\n"
                context += "\nShare this loyalty information with the customer positively."
            
            elif "success" in agent_result:
                # Action result (payment, return, refund, etc.)
                if agent_result.get('success'):
                    context += f"\n\n=== ACTION COMPLETED ===\n"
                    for key, value in agent_result.items():
                        if key != 'success':
                            context += f"{key.replace('_', ' ').title()}: {value}\n"
                    context += "\nConfirm this action to the customer positively."
                else:
                    context += f"\n\n=== ACTION FAILED ===\n"
                    context += f"Error: {agent_result.get('error', 'Unknown error')}\n"
                    context += "\nPolitely explain why this action failed and suggest alternatives."
            
            else:
                # Generic dict result
                context += f"\n\n=== AGENT RESULT ===\n{str(agent_result)}"
        else:
            context += f"\n\n=== AGENT RESULT ===\n{str(agent_result)}"
    
    llm_reply = await generate_response(context)
    
    return {
        "reply": llm_reply or "I'm sorry, I couldn't process your request.",
        "agent_used": intent,
        "actions": actions if actions else None
    }
