# db_init.py

from api import create_app
from models import db, MenuItem, Deal
import os

DB_PATH = os.environ.get('DB_PATH', 'tacobot.db')

app = create_app(DB_PATH)

with app.app_context():
    db.drop_all()
    db.create_all()

    # sample menu items
    items = [
        MenuItem(name='Crunchwrap Supreme', category='Tacos', description='Beef, nacho cheese, lettuce, tomato', price=4.99, calories=530),
        MenuItem(name='Cheesy Gordita Crunch', category='Tacos', description='Spicy beef & melted cheese', price=3.99, calories=500),
        MenuItem(name='Bean Burrito', category='Burritos', description='Bean and cheese', price=1.99, calories=350),
        MenuItem(name='Doritos Locos Tacos', category='Tacos', description='Taco with Doritos shell', price=2.49, calories=300),
    ]
    for it in items:
        db.session.add(it)

    # sample deals
    deals = [
        Deal(title='Taco Tuesday Special', details='2 tacos for $3'),
        Deal(title='Late Night Combo', details='Any burrito + drink discount'),
    ]
    for d in deals:
        db.session.add(d)

    db.session.commit()
    print(f"Initialized DB at {DB_PATH} with sample data.")
