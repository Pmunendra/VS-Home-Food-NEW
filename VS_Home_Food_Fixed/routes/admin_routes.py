# ============================================================
#  ADMIN ROUTES — Dashboard, Orders, Users, Products
# ============================================================
import os, json
from flask import (Blueprint, render_template, request, jsonify,
                   session, redirect, url_for, flash, current_app)
from werkzeug.utils import secure_filename
from models.user_model import db, User, ContactMessage
from models.order_model import Order
from models.product_model import Product
from functools import wraps

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin_bp.admin_login'))
        return f(*args, **kwargs)
    return decorated


# ── LOGIN ────────────────────────────────────────────────────
@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('is_admin'):
        return redirect(url_for('admin_bp.dashboard'))
    if request.method == 'POST':
        data     = request.get_json()
        password = (data or {}).get('password', '')
        if password == current_app.config.get('ADMIN_PASSWORD', 'admin123'):
            session['is_admin'] = True
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Invalid admin password'}), 401
    return render_template('admin/login.html')


@admin_bp.route('/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin_bp.admin_login'))


# ── DASHBOARD ────────────────────────────────────────────────
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    from sqlalchemy import func
    from datetime import datetime

    today = datetime.utcnow().date()
    stats = {
        'total_orders'   : Order.query.count(),
        'total_revenue'  : db.session.query(func.sum(Order.grand_total)).scalar() or 0,
        'today_orders'   : Order.query.filter(func.date(Order.created_at) == today).count(),
        'today_revenue'  : db.session.query(func.sum(Order.grand_total)).filter(func.date(Order.created_at) == today).scalar() or 0,
        'pending_orders' : Order.query.filter_by(status='pending').count(),
        'total_users'    : User.query.count(),
        'total_products' : Product.query.count(),
        'out_of_stock'   : Product.query.filter_by(status='out_of_stock').count(),
    }
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html', stats=stats, recent_orders=recent_orders)


# ── ORDERS PAGE ───────────────────────────────────────────────
@admin_bp.route('/orders')
@admin_required
def orders():
    status_filter = request.args.get('status', '')
    search        = request.args.get('q', '').strip()
    date_filter   = request.args.get('date', '')

    q = Order.query
    if status_filter:
        q = q.filter_by(status=status_filter)
    if search:
        q = q.filter(db.or_(
            Order.order_id.ilike(f'%{search}%'),
            Order.customer_name.ilike(f'%{search}%'),
            Order.customer_phone.ilike(f'%{search}%'),
            Order.customer_email.ilike(f'%{search}%'),
        ))
    if date_filter:
        from sqlalchemy import func
        q = q.filter(func.date(Order.created_at) == date_filter)

    all_orders = q.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=all_orders,
                           status_filter=status_filter, search=search, date_filter=date_filter)


# ── USERS PAGE ────────────────────────────────────────────────
@admin_bp.route('/users')
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


# ── PRODUCTS PAGE ─────────────────────────────────────────────
@admin_bp.route('/products')
@admin_required
def products():
    all_products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/products.html', products=all_products)


# ── ADD PRODUCT ───────────────────────────────────────────────
@admin_bp.route('/api/products', methods=['POST'])
@admin_required
def add_product():
    try:
        name        = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        category    = request.form.get('category', 'general').strip()
        emoji       = request.form.get('emoji', '🍱').strip()
        price       = float(request.form.get('price', 0))
        quantity    = int(request.form.get('quantity', 0))
        status      = request.form.get('status', 'in_stock')
        badge       = request.form.get('badge', '').strip()
        is_veg      = request.form.get('is_veg', 'true') == 'true'
        variants_raw= request.form.get('variants', '[]')

        if not name:
            return jsonify({'success': False, 'message': 'Product name is required'}), 400

        # Parse variants JSON
        try:
            variants = json.loads(variants_raw)
        except Exception:
            variants = []

        # Handle image upload
        image_file = ''
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename    = secure_filename(file.filename)
                upload_dir  = os.path.join(current_app.root_path, 'static', 'images', 'products')
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))
                image_file  = filename

        product = Product(
            name=name, description=description, category=category,
            emoji=emoji, image_file=image_file, price=price,
            quantity=quantity, status=status, badge=badge, is_veg=is_veg
        )
        product.set_variants(variants)
        product.auto_status()   # auto out-of-stock if qty=0

        db.session.add(product)
        db.session.commit()
        return jsonify({'success': True, 'product': product.to_dict(), 'message': 'Product added successfully!'})

    except Exception as e:
        db.session.rollback()
        print(f'[ADMIN PRODUCT ADD ERROR] {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


# ── EDIT PRODUCT ──────────────────────────────────────────────
@admin_bp.route('/api/products/<int:product_id>', methods=['PUT'])
@admin_required
def edit_product(product_id):
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({'success': False, 'message': 'Product not found'}), 404

        # Support both form-data (with image) and JSON
        if request.content_type and 'multipart' in request.content_type:
            data = request.form
        else:
            data = request.get_json() or {}

        if data.get('name'):        product.name        = data['name'].strip()
        if data.get('description') is not None: product.description = data['description'].strip()
        if data.get('category'):    product.category    = data['category'].strip()
        if data.get('emoji'):       product.emoji       = data['emoji'].strip()
        if data.get('price'):       product.price       = float(data['price'])
        if data.get('quantity') is not None:
            product.quantity = int(data['quantity'])
        if data.get('status'):      product.status      = data['status']
        if data.get('badge') is not None: product.badge = data.get('badge', '').strip()
        if data.get('is_veg') is not None:
            val = data.get('is_veg')
            product.is_veg = val if isinstance(val, bool) else (val == 'true')
        if data.get('variants'):
            try:
                product.set_variants(json.loads(data['variants']))
            except Exception:
                pass

        # Handle image upload for PUT (form-data only)
        if request.files and 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename   = secure_filename(file.filename)
                upload_dir = os.path.join(current_app.root_path, 'static', 'images', 'products')
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))
                product.image_file = filename

        product.auto_status()
        db.session.commit()
        return jsonify({'success': True, 'product': product.to_dict(), 'message': 'Product updated!'})

    except Exception as e:
        db.session.rollback()
        print(f'[ADMIN PRODUCT EDIT ERROR] {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


# ── DELETE PRODUCT ────────────────────────────────────────────
@admin_bp.route('/api/products/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Product deleted!'})


# ── TOGGLE PRODUCT STATUS ─────────────────────────────────────
@admin_bp.route('/api/products/<int:product_id>/status', methods=['PUT'])
@admin_required
def toggle_product_status(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    data   = request.get_json() or {}
    status = data.get('status', 'in_stock')
    if status not in ('in_stock', 'out_of_stock'):
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
    product.status = status
    db.session.commit()
    return jsonify({'success': True, 'status': product.status})


# ── UPDATE ORDER STATUS ───────────────────────────────────────
@admin_bp.route('/api/orders/<order_id>/status', methods=['PUT'])
@admin_required
def update_status(order_id):
    data   = request.get_json()
    status = data.get('status')
    order  = Order.query.filter_by(order_id=order_id).first()
    if not order:
        return jsonify({'success': False, 'message': 'Order not found'}), 404
    order.status = status
    db.session.commit()
    return jsonify({'success': True, 'order_id': order_id, 'status': status})


# ── ORDER DETAIL API ─────────────────────────────────────────
@admin_bp.route('/api/orders/<order_id>', methods=['GET'])
@admin_required
def order_detail(order_id):
    order = Order.query.filter_by(order_id=order_id).first()
    if not order:
        return jsonify({'success': False, 'message': 'Order not found'}), 404
    return jsonify({'success': True, 'order': order.to_dict()})


# ── STATS API ─────────────────────────────────────────────────
@admin_bp.route('/api/stats')
@admin_required
def stats():
    from sqlalchemy import func
    from datetime import datetime
    today = datetime.utcnow().date()
    return jsonify({
        'total_orders'  : Order.query.count(),
        'total_revenue' : float(db.session.query(func.sum(Order.grand_total)).scalar() or 0),
        'today_orders'  : Order.query.filter(func.date(Order.created_at) == today).count(),
        'today_revenue' : float(db.session.query(func.sum(Order.grand_total)).filter(func.date(Order.created_at) == today).scalar() or 0),
        'pending_orders': Order.query.filter_by(status='pending').count(),
        'total_users'   : User.query.count(),
    })
