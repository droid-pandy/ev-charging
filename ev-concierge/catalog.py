"""
Restaurant/Cafe Menu Catalog
Mock Starbucks-style menu with items and prices
"""

MENU_CATALOG = {
    "drinks": {
        "Large Latte": {
            "name": "Large Latte",
            "price": 5.45,
            "category": "Hot Coffee",
            "size": "Grande",
            "description": "Rich espresso with steamed milk"
        },
        "Cappuccino": {
            "name": "Cappuccino",
            "price": 4.95,
            "category": "Hot Coffee",
            "size": "Grande",
            "description": "Espresso with foamed milk"
        },
        "Americano": {
            "name": "Americano",
            "price": 3.95,
            "category": "Hot Coffee",
            "size": "Grande",
            "description": "Espresso shots with hot water"
        },
        "Espresso": {
            "name": "Espresso",
            "price": 2.95,
            "category": "Hot Coffee",
            "size": "Double Shot",
            "description": "Rich, full-bodied espresso"
        },
        "Iced Coffee": {
            "name": "Iced Coffee",
            "price": 4.25,
            "category": "Cold Coffee",
            "size": "Grande",
            "description": "Freshly brewed and served over ice"
        },
        "Cold Brew": {
            "name": "Cold Brew",
            "price": 4.95,
            "category": "Cold Coffee",
            "size": "Grande",
            "description": "Slow-steeped, smooth and sweet"
        },
        "Caramel Macchiato": {
            "name": "Caramel Macchiato",
            "price": 5.95,
            "category": "Hot Coffee",
            "size": "Grande",
            "description": "Vanilla, steamed milk, espresso, and caramel"
        },
        "Green Tea": {
            "name": "Green Tea",
            "price": 3.45,
            "category": "Tea",
            "size": "Grande",
            "description": "Premium green tea"
        },
        "Hot Chocolate": {
            "name": "Hot Chocolate",
            "price": 4.45,
            "category": "Hot Drinks",
            "size": "Grande",
            "description": "Steamed milk with mocha sauce"
        }
    },
    "food": {
        "Turkey Sandwich": {
            "name": "Turkey Sandwich",
            "price": 7.95,
            "category": "Sandwiches",
            "description": "Turkey, cheese, lettuce on artisan bread"
        },
        "Chicken Wrap": {
            "name": "Chicken Wrap",
            "price": 8.45,
            "category": "Sandwiches",
            "description": "Grilled chicken with veggies in a wrap"
        },
        "Caesar Salad": {
            "name": "Caesar Salad",
            "price": 7.45,
            "category": "Salads",
            "description": "Romaine, parmesan, croutons, Caesar dressing"
        },
        "Veggie Burger": {
            "name": "Veggie Burger",
            "price": 8.95,
            "category": "Sandwiches",
            "description": "Plant-based patty with fresh toppings"
        },
        "Breakfast Burrito": {
            "name": "Breakfast Burrito",
            "price": 6.95,
            "category": "Breakfast",
            "description": "Eggs, cheese, potatoes, and salsa"
        },
        "Bagel with Cream Cheese": {
            "name": "Bagel with Cream Cheese",
            "price": 3.95,
            "category": "Breakfast",
            "description": "Fresh bagel with cream cheese"
        },
        "Fruit & Yogurt Parfait": {
            "name": "Fruit & Yogurt Parfait",
            "price": 5.45,
            "category": "Breakfast",
            "description": "Greek yogurt with berries and granola"
        },
        "Chocolate Chip Cookie": {
            "name": "Chocolate Chip Cookie",
            "price": 2.95,
            "category": "Bakery",
            "description": "Warm, gooey chocolate chip cookie"
        },
        "Blueberry Muffin": {
            "name": "Blueberry Muffin",
            "price": 3.45,
            "category": "Bakery",
            "description": "Fresh baked with real blueberries"
        },
        "Avocado Toast": {
            "name": "Avocado Toast",
            "price": 6.95,
            "category": "Breakfast",
            "description": "Smashed avocado on multigrain toast"
        }
    }
}


def get_drink_names():
    """Get list of all drink names"""
    return list(MENU_CATALOG["drinks"].keys())


def get_food_names():
    """Get list of all food names"""
    return list(MENU_CATALOG["food"].keys())


def get_item_price(item_name):
    """Get price for a specific item"""
    # Check drinks
    if item_name in MENU_CATALOG["drinks"]:
        return MENU_CATALOG["drinks"][item_name]["price"]
    # Check food
    if item_name in MENU_CATALOG["food"]:
        return MENU_CATALOG["food"][item_name]["price"]
    return None


def get_item_details(item_name):
    """Get full details for a specific item"""
    # Check drinks
    if item_name in MENU_CATALOG["drinks"]:
        return MENU_CATALOG["drinks"][item_name]
    # Check food
    if item_name in MENU_CATALOG["food"]:
        return MENU_CATALOG["food"][item_name]
    return None


def calculate_order_total(items):
    """Calculate total price for a list of items"""
    total = 0.0
    for item_name in items:
        price = get_item_price(item_name)
        if price:
            total += price
    return round(total, 2)


def get_menu_by_category(category_type="all"):
    """Get menu items filtered by category"""
    if category_type == "drinks":
        return MENU_CATALOG["drinks"]
    elif category_type == "food":
        return MENU_CATALOG["food"]
    else:
        return MENU_CATALOG
