# api.py

from flask import Flask, jsonify, request, abort
from models import db, MenuItem, Deal, Order, OrderItem, Feedback
import os

def create_app(db_path=None):
    app = Flask(__name__)
    if db_path:
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tacobot.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/api/menu', methods=['GET'])
    def get_menu():
        category = request.args.get('category')
        if category:
            items = MenuItem.query.filter_by(category=category).all()
        else:
            items = MenuItem.query.all()
        return jsonify([{
            'id': it.id,
            'name': it.name,
            'category': it.category,
            'description': it.description,
            'price': it.price,
            'calories': it.calories
        } for it in items])

    @app.route('/api/menu/item/<string:item_name>', methods=['GET'])
    def get_item(item_name):
        it = MenuItem.query.filter(MenuItem.name.ilike(item_name)).first()
        if not it:
            abort(404)
        return jsonify({
            'id': it.id,
            'name': it.name,
            'category': it.category,
            'description': it.description,
            'price': it.price,
            'calories': it.calories
        })

    @app.route('/api/deals', methods=['GET'])
    def get_deals():
        deals = Deal.query.filter_by(active=True).all()
        return jsonify([{'id': d.id, 'title': d.title, 'details': d.details} for d in deals])

    @app.route('/api/order/add', methods=['POST'])
    def add_order_item():
        data = request.json or {}
        discord_user_id = data.get('discord_user_id')
        item_name = data.get('item_name')
        quantity = data.get('quantity', 1)

        if not discord_user_id or not item_name:
            return jsonify({'error': 'discord_user_id and item_name required'}), 400

        menu_item = MenuItem.query.filter(MenuItem.name.ilike(item_name)).first()
        if not menu_item:
            return jsonify({'error': 'item not found'}), 404

        # get or create order
        order = Order.query.filter_by(discord_user_id=discord_user_id, checked_out=False).first()
        if not order:
            order = Order(discord_user_id=discord_user_id)
            db.session.add(order)
            db.session.commit()

        # check if item already in order
        existing = OrderItem.query.filter_by(order_id=order.id, menu_item_id=menu_item.id).first()
        if existing:
            existing.quantity += int(quantity)
        else:
            oi = OrderItem(order_id=order.id, menu_item_id=menu_item.id, quantity=int(quantity))
            db.session.add(oi)
        db.session.commit()

        return jsonify({'message': 'added', 'order_id': order.id})

    @app.route('/api/order/view', methods=['GET'])
    def view_order():
        discord_user_id = request.args.get('discord_user_id')
        if not discord_user_id:
            return jsonify({'error': 'discord_user_id required'}), 400

        order = Order.query.filter_by(discord_user_id=discord_user_id, checked_out=False).first()
        if not order:
            return jsonify({'items': []})
        items = []
        total = 0.0
        for oi in order.items:
            mi = oi.menu_item
            items.append({
                'name': mi.name,
                'quantity': oi.quantity,
                'price': mi.price,
                'subtotal': mi.price * oi.quantity
            })
            total += mi.price * oi.quantity
        return jsonify({'order_id': order.id, 'items': items, 'total': total})

    @app.route('/api/order/checkout', methods=['POST'])
    def checkout():
        data = request.json or {}
        discord_user_id = data.get('discord_user_id')
        if not discord_user_id:
            return jsonify({'error': 'discord_user_id required'}), 400
        order = Order.query.filter_by(discord_user_id=discord_user_id, checked_out=False).first()
        if not order:
            return jsonify({'error': 'no active order'}), 404
        order.checked_out = True
        db.session.commit()
        return jsonify({'message': 'checked out', 'order_id': order.id})

    @app.route('/api/feedback', methods=['POST'])
    def feedback():
        data = request.json or {}
        discord_user_id = data.get('discord_user_id')
        message = data.get('message')
        if not discord_user_id or not message:
            return jsonify({'error': 'discord_user_id and message required'}), 400
        fb = Feedback(discord_user_id=discord_user_id, message=message)
        db.session.add(fb)
        db.session.commit()
        return jsonify({'message': 'thanks'})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
