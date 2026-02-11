import re
from typing import Optional


def extract_product_name(message: str) -> Optional[str]:
    """
    Extract product name from a message, removing action keywords.
    Examples:
    - "Add the Adidas shirt to cart" → "Adidas shirt"
    - "show me Nike shoes" → "Nike shoes"
    - "I want the iPhone" → "iPhone"
    """
    message_cleaned = message.lower()
    
    # Remove common action/filler words
    remove_words = [
        "add", "put", "place", "to", "the", "a", "an", "my", "in", "into",
        "cart", "shopping cart", "basket", "available", "stock", "check",
        "is there", "do you have", "show me", "find", "search", "for",
        "i want", "i need", "i'll take", "give me", "get me", "this", "that"
    ]
    
    # Replace each word/phrase
    for word in remove_words:
        message_cleaned = re.sub(r'\b' + re.escape(word) + r'\b', '', message_cleaned, flags=re.IGNORECASE)
    
    # Clean up extra spaces
    message_cleaned = re.sub(r'\s+', ' ', message_cleaned).strip()
    
    return message_cleaned if message_cleaned else None


def extract_order_id(message: str) -> Optional[str]:
    """
    Extract order ID from message. Supports multiple formats:
    - Full UUID: "550e8400-e29b-41d4-a716-446655440000"
    - Short numeric: "order 12345" or "order #12345"
    - Alphanumeric: "ORD-123" or "ORDER123"
    """
    message = message.strip()
    
    # Try common order ID patterns
    patterns = [
        r'order[:\s#-]+([a-zA-Z0-9\-]{3,})',  # "order 123", "order #123", "order: ABC-123"
        r'#([a-zA-Z0-9\-]{3,})',              # "#12345" or "#ORD-123"
        r'\b([a-fA-F0-9\-]{30,})\b',          # Full UUID format
        r'\b(ORD-\d+)\b',                      # ORD-12345 format
        r'\b(ORDER\d+)\b',                     # ORDER12345 format
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1).upper()  # Return uppercase for consistency
    
    # Fallback: check if message contains standalone number (3+ digits)
    words = message.split()
    for word in words:
        cleaned = word.strip('#:')
        if cleaned.isdigit() and len(cleaned) >= 3:
            return cleaned
    
    return None
