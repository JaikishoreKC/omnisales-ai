from typing import Dict, List

INTENT_KEYWORDS: Dict[str, List[str]] = {
    "recommendation": ["suggest", "recommend", "best", "top", "popular", "help me find", "looking for", "show me"],
    "inventory": ["available", "stock", "in stock", "do you have", "any left", "check stock"],
    "cart": ["cart", "add this", "i want this", "i'll take", "put in", "view cart", "my cart", "show cart", "remove from cart", "clear cart"],
    "payment": ["buy", "purchase", "checkout", "pay", "complete order", "place order", "proceed to payment"],
    "tracking": ["track", "where is", "delivery", "shipped", "order status", "when will", "arrive"],
    "loyalty": ["points", "reward", "loyalty", "discount", "coupon", "offer", "deal", "redeem", "tier", "membership"],
    "post_purchase": ["return", "refund", "exchange", "cancel", "complaint", "issue", "problem", "defect", "broken", "wrong", "damaged"],
    "proactive": ["call me", "phone", "follow up", "remind", "schedule", "abandoned cart"],
    "pos_sync": ["pos", "store system", "sync inventory", "in-store"]
}


def detect_intent(message: str) -> str:
    if not message:
        return "general"
    
    message_lower = message.lower()
    
    # Priority checks - more specific intents first
    
    # Loyalty offers (check before recommendation)
    if "offer" in message_lower or "coupon" in message_lower or "deal" in message_lower:
        return "loyalty"
    
    # Cart operations (must check before general keywords)
    cart_keywords = INTENT_KEYWORDS["cart"]
    if any(kw in message_lower for kw in cart_keywords):
        return "cart"

    if "i want" in message_lower and any(term in message_lower for term in ["too", "also", "another", "as well"]):
        return "cart"

    if "add " in message_lower and any(term in message_lower for term in ["too", "also", "another", "as well"]):
        return "cart"
    
    if any(term in message_lower for term in ["cart", "basket"]) and any(
        verb in message_lower for verb in ["add", "put", "remove", "delete", "clear", "empty"]
    ):
        return "cart"
    
    # Check other intents
    for intent, keywords in INTENT_KEYWORDS.items():
        if intent in ["cart", "loyalty"]:  # Skip cart and loyalty, we already handled them
            continue
        if any(kw in message_lower for kw in keywords):
            return intent
    
    return "general"
