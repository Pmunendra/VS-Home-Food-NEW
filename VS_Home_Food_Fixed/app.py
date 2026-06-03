from flask import Flask, render_template, session, redirect, url_for, flash
from config import Config
from models.user_model import db
from models.product_model import Product
from services.notification_service import mail

app = Flask(__name__)
app.config.from_object(Config)

# ── Init Extensions ──────────────────────────────────────────
db.init_app(app)
mail.init_app(app)

# ── Register Blueprints ──────────────────────────────────────
from routes.order_routes   import order_bp
from routes.auth_routes    import auth_bp
from routes.product_routes import product_bp
from routes.admin_routes   import admin_bp
app.register_blueprint(order_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(product_bp)
app.register_blueprint(admin_bp)

# ── Create DB tables on first run ────────────────────────────
with app.app_context():
    db.create_all()
    print("[DB] Tables created / verified ✅")
    # Ensure product images directory exists
    import os
    os.makedirs(os.path.join(app.root_path, 'static', 'images', 'products'), exist_ok=True)

# ── CONTEXT PROCESSOR — inject user into all templates ───────
@app.context_processor
def inject_user():
    user_id   = session.get('user_id')
    user_name = session.get('user_name', '')
    user_email= session.get('user_email', '')
    return dict(
        session_user_id   = user_id,
        session_user_name = user_name,
        session_user_email= user_email,
        logged_in         = bool(user_id)
    )

# ── PAGE ROUTES ──────────────────────────────────────────────
@app.route('/')
def home():       return render_template('index.html')

@app.route('/menu')
def menu():       return render_template('menu.html')

@app.route('/product/<int:product_id>')
def product(product_id): return render_template('product.html', product_id=product_id)

@app.route('/cart')
def cart():       return render_template('cart.html')

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/login')
def login():
    if session.get('user_id'):
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/register')
def register():
    if session.get('user_id'):
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/order-success')
def order_success(): return render_template('order-success.html')

@app.route('/profile')
def profile():
    if not session.get('user_id'):
        flash('Please login to view your profile.', 'warning')
        return redirect(url_for('login'))
    from models.user_model import User
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/my-orders')
def my_orders():
    if not session.get('user_id'):
        flash('Please login to view your orders.', 'warning')
        return redirect(url_for('login'))
    from models.order_model import Order
    orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.created_at.desc()).all()
    return render_template('my-orders.html', orders=orders)

# ── ADMIN ROUTES ─────────────────────────────────────────────
@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return redirect(url_for('admin_bp.admin_login'))
    return redirect(url_for('admin_bp.dashboard'))

# ── ERROR HANDLERS ───────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
