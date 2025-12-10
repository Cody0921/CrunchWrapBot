# api.py
from flask import Flask, jsonify, request
from models import db, MenuItem, Deal, Order, OrderItem, Feedback
import os
import random
import time

def create_app(db_path=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}" if db_path else 'sqlite:///FastFoodNutrition.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # ---------------- MENU ----------------
    @app.route('/api/menu', methods=['GET'])
    def get_menu():
        category = request.args.get('category')
        limit = int(request.args.get('limit', 10))
        query = MenuItem.query
        if category:
            query = query.filter(MenuItem.category.ilike(category))
        items = query.limit(limit).all()
        time.sleep(random.uniform(0.2, 0.8))
        return jsonify([
            {
                'id': it.id,
                'name': it.name,
                'company': "Taco Bell",  
                'calories': it.calories,
                'price': it.price,
                'category': it.category
            } for it in items
        ])

    # ---------------- ITEM DETAILS ----------------
    @app.route('/api/menu/item/<string:item_name>', methods=['GET'])
    def get_item(item_name):
        it = MenuItem.query.filter(MenuItem.name.ilike(item_name)).first()
        if not it:
            return jsonify({'error': 'Item not found'}), 404
        time.sleep(random.uniform(0.2, 0.5))
        return jsonify({
            'id': it.id,
            'name': it.name,
            'company': "Taco Bell",  
            'calories': it.calories,
            'price': it.price,
            'category': it.category
        })

    # ---------------- DEALS ----------------
    @app.route('/api/deals', methods=['GET'])
    def get_deals():
        deals = Deal.query.filter_by(active=True).all()
        return jsonify([{'id': d.id, 'title': d.title, 'details': d.details} for d in deals])

    # ---------------- ORDER ----------------
    @app.route('/api/order/add', methods=['POST'])
    def add_order_item():
        data = request.json or {}
        user_id = data.get('discord_user_id')
        item_name = data.get('item_name')
        quantity = int(data.get('quantity', 1))

        if not user_id or not item_name:
            return jsonify({'error': 'discord_user_id and item_name required'}), 400

        menu_item = MenuItem.query.filter(MenuItem.name.ilike(item_name)).first()
        if not menu_item:
            return jsonify({'error': 'item not found'}), 404

        order = Order.query.filter_by(discord_user_id=user_id, checked_out=False).first()
        if not order:
            order = Order(discord_user_id=user_id)
            db.session.add(order)
            db.session.commit()

        existing = OrderItem.query.filter_by(order_id=order.id, menu_item_id=menu_item.id).first()
        if existing:
            existing.quantity += quantity
        else:
            oi = OrderItem(order_id=order.id, menu_item_id=menu_item.id, quantity=quantity)
            db.session.add(oi)

        db.session.commit()
        return jsonify({'message': 'added', 'order_id': order.id})

    @app.route('/api/order/view', methods=['GET'])
    def view_order():
        user_id = request.args.get('discord_user_id')
        if not user_id:
            return jsonify({'error': 'discord_user_id required'}), 400

        order = Order.query.filter_by(discord_user_id=user_id, checked_out=False).first()
        if not order:
            return jsonify({'items': []})

        items = []
        total = 0.0
        for oi in order.items:
            mi = oi.menu_item
            subtotal = mi.price * oi.quantity
            items.append({
                'name': mi.name,
                'quantity': oi.quantity,
                'price': mi.price,
                'subtotal': subtotal
            })
            total += subtotal
        return jsonify({'order_id': order.id, 'items': items, 'total': total})

    @app.route('/api/order/checkout', methods=['POST'])
    def checkout():
        data = request.json or {}
        user_id = data.get('discord_user_id')
        if not user_id:
            return jsonify({'error': 'discord_user_id required'}), 400

        order = Order.query.filter_by(discord_user_id=user_id, checked_out=False).first()
        if not order:
            return jsonify({'error': 'no active order'}), 404

        order.checked_out = True
        db.session.commit()
        return jsonify({'message': 'checked out', 'order_id': order.id})

    # ---------------- FEEDBACK ----------------
    @app.route('/api/feedback', methods=['POST'])
    def feedback():
        data = request.json or {}
        user_id = data.get('discord_user_id')
        message = data.get('message')
        if not user_id or not message:
            return jsonify({'error': 'discord_user_id and message required'}), 400

        fb = Feedback(discord_user_id=user_id, message=message)
        db.session.add(fb)
        db.session.commit()
        return jsonify({'message': 'thanks'})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)

