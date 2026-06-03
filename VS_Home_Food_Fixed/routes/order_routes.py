# ============================================================
#  ORDER ROUTES — COD only with AUTHENTICATION REQUIREMENT
# ============================================================
from flask import Blueprint, request, jsonify, session
from models.user_model import db, User
from models.order_model import Order
from services.notification_service import notify_order_placed
import random, string
from datetime import datetime

order_bp = Blueprint('orders', __name__)

def generate_order_id():
    """Generate unique order ID"""
    suffix = ''.join(random.choices(string.digits, k=5))
    return f"VS{datetime.now().strftime('%y%m%d')}{suffix}"


@order_bp.route('/api/order/place', methods=['POST'])
def place_order():
    """
    Place an order - REQUIRES AUTHENTICATION
    
    Authentication Flow:
    1. Check if user is logged in
    2. If not logged in, return 401 (frontend will show login modal)
    3. If logged in, proceed with order
    """
    try:
        # STEP 1: Check authentication
        user_id = session.get('user_id')
        if not user_id:
            print("[ORDER] ❌ Unauthorized attempt to place order (no user_id in session)")
            return jsonify({
                'success': False,
                'message': 'Authentication required. Please login to continue.',
                'requires_auth': True
            }), 401

        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            session.clear()
            print("[ORDER] ❌ User not found for id:", user_id)
            return jsonify({
                'success': False,
                'message': 'User session invalid. Please login again.',
                'requires_auth': True
            }), 401

        # STEP 2: Get order data
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data received'}), 400

        # Get customer email (from form or session)
        customer_email = data.get('email', '').strip()
        if not customer_email:
            customer_email = session.get('user_email', user.email)
        
        if not customer_email:
            return jsonify({
                'success': False,
                'message': 'Email address required for order confirmation'
            }), 400

        # STEP 3: Validate cart items
        order_id = generate_order_id()
        items = data.get('items', [])
        
        if not items:
            return jsonify({'success': False, 'message': 'Cart is empty'}), 400

        # Process items
        for item in items:
            item['total'] = float(item.get('price', 0)) * int(item.get('qty', 1))
            item['emoji'] = item.get('emoji', '🍱')
            item['weight'] = item.get('weight', '')

        subtotal = sum(i['total'] for i in items)
        grand_total = subtotal + 40  # delivery charge

        # STEP 4: Create order record
        order_data = {
            'order_id': order_id,
            'customer_email': customer_email,
            'items': items,
            'address': {
                'name': data.get('fullName', ''),
                'phone': data.get('phone', ''),
                'line1': data.get('address1', ''),
                'line2': data.get('address2', ''),
                'city': data.get('city', ''),
                'pincode': data.get('pincode', ''),
            },
            'payment_method': 'Cash on Delivery',  # COD only
            'grand_total': grand_total,
            'instructions': data.get('instructions', ''),
        }

        order = Order(
            order_id=order_id,
            user_id=user_id,  # IMPORTANT: Associate order with logged-in user
            customer_email=customer_email,
            customer_name=data.get('fullName', ''),
            customer_phone=data.get('phone', ''),
            address_line1=data.get('address1', ''),
            address_line2=data.get('address2', ''),
            city=data.get('city', ''),
            pincode=data.get('pincode', ''),
            payment_method='Cash on Delivery',
            grand_total=grand_total,
            instructions=data.get('instructions', ''),
            status='pending',
        )
        order.set_items(items)
        
        db.session.add(order)
        db.session.commit()
        print(f"[ORDER] ✅ Saved: {order_id} for user: {user.email}")

        # STEP 5: Send notifications
        notify_results = notify_order_placed(order_data)
        print(f"[ORDER] Notifications: {notify_results}")

        return jsonify({
            'success': True,
            'order_id': order_id,
            'grand_total': grand_total,
            'notifications': notify_results,
            'message': 'Order placed successfully!'
        })

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        print(f"[ORDER ERROR] {e}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@order_bp.route('/api/orders', methods=['GET'])
def get_all_orders():
    """Get all orders (admin view)"""
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify({'orders': [o.to_dict() for o in orders]})


@order_bp.route('/api/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update order status (admin only)"""
    data = request.get_json()
    new_status = data.get('status')
    
    order = Order.query.filter_by(order_id=order_id).first()
    if not order:
        return jsonify({'success': False, 'message': 'Order not found'}), 404
    
    order.status = new_status
    db.session.commit()
    
    return jsonify({
        'success': True,
        'order_id': order_id,
        'status': new_status
    })


@order_bp.route('/api/stats', methods=['GET'])
def get_stats():
    """Get order statistics"""
    from sqlalchemy import func
    today = datetime.utcnow().date()
    
    return jsonify({
        'total_orders': Order.query.count(),
        'total_revenue': float(
            db.session.query(func.sum(Order.grand_total)).scalar() or 0
        ),
        'today_orders': Order.query.filter(
            func.date(Order.created_at) == today
        ).count(),
        'today_revenue': float(
            db.session.query(func.sum(Order.grand_total)).filter(
                func.date(Order.created_at) == today
            ).scalar() or 0
        ),
        'pending_orders': Order.query.filter_by(status='pending').count(),
    })
