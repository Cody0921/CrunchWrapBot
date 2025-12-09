# db_init.py
from api import create_app
from models import db, MenuItem, Deal
import os
import sqlite3
import random

DB_PATH = os.environ.get('DB_PATH', 'FastFoodNutrition.db')
app = create_app(DB_PATH)

def safe_int(val):
    """Convert value to int safely, return None if invalid."""
    try:
        val = str(val).replace('\xa0', '').strip()
        return int(val)
    except:
        return None

def assign_category(item_name: str) -> str:
    """Assign a realistic category based on keywords, only include proper drinks."""
    name = item_name.lower()
    if "taco" in name:
        return "Tacos"
    elif "burrito" in name:
        return "Burritos"
    elif "nacho" in name or "fries" in name:
        return "Sides"
    elif ("20 fl oz" in name or "30 fl oz" in name) and "baja" in name:
        return "Drinks"
    elif "dessert" in name or "cookie" in name or "cake" in name:
        return "Desserts"
    elif "sandwich" in name or "wrap" in name:
        return "Sandwiches"
    elif "salad" in name:
        return "Salads"
    else:
        return "Misc"

def assign_price(category: str) -> float:
    """Return a realistic random price based on category."""
    category = category.lower()
    if category == "tacos":
        return round(random.uniform(2.0, 4.5), 2)
    elif category == "burritos":
        return round(random.uniform(3.0, 6.0), 2)
    elif category == "sides":
        return round(random.uniform(1.5, 3.5), 2)
    elif category == "drinks":
        return round(random.uniform(2.0, 3.5), 2)  # realistic Baja Blast price
    elif category == "desserts":
        return round(random.uniform(1.5, 4.0), 2)
    elif category == "sandwiches":
        return round(random.uniform(3.5, 6.5), 2)
    elif category == "salads":
        return round(random.uniform(3.5, 6.0), 2)
    else:  # Misc
        return round(random.uniform(2.0, 5.0), 2)

def populate_menu():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT Item, Calories FROM FastFoodNutrition")
    rows = cursor.fetchall()

    with app.app_context():
        db.drop_all()
        db.create_all()

        # Add menu items, all company = "Taco Bell"
        added_count = 0
        for item, calories in rows:
            category = assign_category(item)
            if category == "Drinks" or category != "Drinks":  # include all except drinks without size
                # Skip drinks that don't meet size requirement
                if "drink" in item.lower() and category != "Drinks":
                    continue
                menu_item = MenuItem(
                    company="Taco Bell",
                    name=item,
                    calories=safe_int(calories),
                    price=assign_price(category),
                    category=category
                )
                db.session.add(menu_item)
                added_count += 1

        # Add sample deals
        deals = [
            Deal(title="Taco Tuesday Special", details="2 tacos for $3"),
            Deal(title="Late Night Combo", details="Any burrito + drink discount"),
            Deal(title="Dessert Deal", details="Buy 1 dessert, get 1 free"),
        ]
        for d in deals:
            db.session.add(d)

        db.session.commit()
    conn.close()
    print(f"Database initialized with {added_count} Taco Bell menu items and {len(deals)} deals.")

if __name__ == "__main__":
    populate_menu()
