from typing import Dict, List

INTENT_KEYWORDS: Dict[str, List[str]] = {
    "recommendation": ["suggest", "recommend", "best", "top", "popular", "help me find", "looking for", "show me"],
    "inventory": ["available", "stock", "in stock", "do you have", "any left", "check stock"],
    "payment": ["buy", "purchase", "order", "checkout", "pay", "cart", "add to cart"],
    "tracking": ["track", "where is", "delivery", "shipped", "order status", "when will", "arrive"],
    "loyalty": ["points", "reward", "discount", "coupon", "offer", "deal"],
    "post_purchase": ["return", "refund", "exchange", "cancel", "complaint", "issue", "problem"]
}


def detect_intent(message: str) -> str:
    if not message:
        return "general"
    
    message_lower = message.lower()
    
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in message_lower for kw in keywords):
            return intent
    
    return "general"
