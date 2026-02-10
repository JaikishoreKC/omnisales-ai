import asyncio
import random
import uuid
from app.core.database import connect_db, close_db, get_database

CATEGORIES = {
    "shirts": ["T-Shirt", "Polo Shirt", "Dress Shirt", "Henley", "Tank Top", "Button-Up"],
    "shoes": ["Sneakers", "Boots", "Sandals", "Loafers", "Running Shoes", "Oxfords"],
    "jeans": ["Skinny Jeans", "Slim Fit Jeans", "Straight Jeans", "Bootcut Jeans", "Relaxed Fit"],
    "electronics": ["Headphones", "Smart Watch", "Tablet", "Bluetooth Speaker", "Power Bank", "USB Cable"]
}

BRANDS = ["Nike", "Adidas", "Puma", "Reebok", "Sony", "Samsung", "Apple", "LG", "Dell", "HP"]
COLORS = ["Black", "White", "Blue", "Red", "Green", "Gray", "Brown", "Navy", "Beige"]
ADJECTIVES = ["Premium", "Classic", "Modern", "Vintage", "Sport", "Casual", "Luxury", "Essential"]


def generate_product(category: str, product_type: str):
    brand = random.choice(BRANDS)
    color = random.choice(COLORS)
    adjective = random.choice(ADJECTIVES)
    name = f"{adjective} {brand} {product_type} - {color}"
    
    if category == "electronics":
        price = round(random.uniform(29.99, 499.99), 2)
    elif category == "shoes":
        price = round(random.uniform(39.99, 199.99), 2)
    elif category == "jeans":
        price = round(random.uniform(29.99, 129.99), 2)
    else:
        price = round(random.uniform(19.99, 89.99), 2)
    
    stock = random.randint(0, 100)
    
    return {
        "product_id": str(uuid.uuid4()),
        "name": name,
        "category": category,
        "price": price,
        "stock": stock
    }


async def load_products():
    await connect_db()
    db = get_database()
    products_collection = db.products
    
    await products_collection.delete_many({})
    
    products = []
    for _ in range(200):
        category = random.choice(list(CATEGORIES.keys()))
        product_type = random.choice(CATEGORIES[category])
        product = generate_product(category, product_type)
        products.append(product)
    
    result = await products_collection.insert_many(products)
    
    print(f"Inserted {len(result.inserted_ids)} products")
    
    await close_db()


if __name__ == "__main__":
    asyncio.run(load_products())
