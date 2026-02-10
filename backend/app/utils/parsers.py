import re
from typing import Optional


def extract_product_name(message: str) -> Optional[str]:
    message_cleaned = message.lower()
    for keyword in ["available", "stock", "check", "is there", "do you have"]:
        message_cleaned = message_cleaned.replace(keyword, "")
    return message_cleaned.strip() or None


def extract_order_id(message: str) -> Optional[str]:
    words = message.split()
    for word in words:
        if len(word) > 20 and re.match(r'^[a-f0-9\-]{30,}$', word, re.IGNORECASE):
            return word
    return None
