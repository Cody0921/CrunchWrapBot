# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    calories = db.Column(db.Integer, nullable=True)
    price = db.Column(db.Float, default=0.0)
    category = db.Column(db.String, default="Misc")

class Deal(db.Model):
    __tablename__ = 'deals'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    details = db.Column(db.String, nullable=True)
    active = db.Column(db.Boolean, default=True)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    discord_user_id = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    checked_out = db.Column(db.Boolean, default=False)
    items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'))
    quantity = db.Column(db.Integer, default=1)
    order = db.relationship('Order', back_populates='items')
    menu_item = db.relationship('MenuItem')

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    discord_user_id = db.Column(db.String, nullable=False)
    message = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
