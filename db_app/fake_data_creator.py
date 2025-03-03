import os
import boto3
import random
from faker import Faker
from decimal import Decimal

# Initialize Faker
fake = Faker()

dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_REGION'))

customers_table = dynamodb.Table('customers')
purchases_table = dynamodb.Table('purchases')
products_table = dynamodb.Table('products')

product_names = [
    "Arabica Bliss", "Espresso Elite", "Colombian Gold", "Mocha Magic", "Latte Supreme",
    "Dark Roast", "Vanilla Brew", "Hazelnut Delight", "French Roast", "Morning Blend",
    "Signature Espresso", "Caramel Kiss", "Nutty Aroma", "Brazilian Bold", "Cinnamon Swirl",
    "House Blend", "Velvet Brew", "Chocolate Mocha", "Pumpkin Spice", "Maple Roast",
    "Peruvian Classic", "Organic Bliss", "Golden Espresso", "Berry Infused", "Midnight Roast",
    "Toffee Latte", "Hazel Brew", "Vanilla Espresso", "Choco Hazelnut", "Italian Roast",
    "Ethiopian Gem", "Silky Mocha", "Coconut Cream", "Signature Roast", "Café Caramel",
    "Bold Classic", "Velvet Dark", "Morning Joy", "Cinnamon Roast", "Winter Spice",
    "Rich Espresso", "Dark Elegance", "Toasted Almond", "Creamy Delight", "Espresso Shot",
    "Colombian Classic", "Jamaican Bliss", "Nutty Brew", "Sweet Mocha", "Chocolate Cream",
    "Turkish Delight", "Spiced Roast", "Holiday Blend", "Classic Americano", "Caramel Crunch",
    "Deep Roast", "Aromatic Joy", "Cappuccino Love", "Black Gold", "Signature Beans",
    "Morning Espresso", "Honey Latte", "Smooth Roast", "Colombian Rich", "Dark Crema",
    "Frothy Mocha", "Mild Roast", "Barista Blend", "Creamy Cocoa", "Almond Joy",
    "Bali Beans", "Vienna Roast", "Robusta Rich", "Cafe Classic", "Italian Passion",
    "Mild Arabica", "Organic Roast", "Pure Espresso", "Cuban Bold", "Choco Delight",
    "Colombian Reserve", "Cinnamon Cream", "Golden Latte", "Peppermint Mocha", "Spiced Latte",
    "Dark Heritage", "Ethiopian Roast", "Barista Touch", "Gourmet Bliss", "Coffee Mug",
    "Travel Tumbler", "Espresso Cups", "French Press", "Coffee Grinder", "Milk Frother",
    "Bamboo Stirrers", "Cold Brew Kit", "Coffee Warmer", "Reusable Pods", "Coffee Canister"
]

def create_fake_customer():
    """Generate a fake customer record with email as primary key."""
    email = fake.email()
    return {
        'email': email,
        'name': fake.first_name(),
        'surname': fake.last_name(),
        'address': fake.address()
    }

def create_fake_product(product_name):
    """Generate a fake product with a predefined name."""
    return {
        'product_name': product_name,
        'price': Decimal(str(round(random.uniform(5, 500), 2))),  # Convert price to Decimal
        'available_amount': random.randint(10, 100)  # Random stock amount
    }

def create_fake_purchase(customers, products):
    """Generate a fake purchase linking an existing customer and products."""
    customer = random.choice(customers)  # Pick a random customer
    num_products = random.randint(1, min(5, len(products)))  # Limit to available products
    selected_products = random.sample(products, num_products)  # Ensure valid sampling

    total_price = Decimal('0')
    product_items = []  # List of dictionaries containing product name and quantity

    for product in selected_products:
        amount = random.randint(1, 5)  # Random quantity per product
        item_total = Decimal(str(product['price'])) * Decimal(str(amount))  # Safe Decimal conversion
        total_price += item_total

        product_items.append({
            'product_name': product['product_name'],  # Correct key name
            'amount': amount
        })

    return {
        'purchase_id': fake.uuid4(),
        'customer_email': customer['email'],
        'products': product_items,  # Now stores a list of dictionaries
        'total_price': total_price
    }

def insert_fake_data(num_customers=50, num_purchases=70):
    """Insert fake customers, products, and purchases into DynamoDB."""

    # Generate customers
    customers = [create_fake_customer() for _ in range(num_customers)]
    for customer in customers:
        customers_table.put_item(Item=customer)
    print(f"Inserted {num_customers} customers.")

    # Generate products from the predefined list
    products = [create_fake_product(name) for name in product_names]
    for product in products:
        products_table.put_item(Item=product)
    print(f"Inserted {len(product_names)} products.")

    # Generate purchases
    purchases = [create_fake_purchase(customers, products) for _ in range(num_purchases)]
    for purchase in purchases:
        purchases_table.put_item(Item=purchase)
    print(f"Inserted {num_purchases} purchases.")
    
# Run the function once
if __name__ == "__main__":
    insert_fake_data()
