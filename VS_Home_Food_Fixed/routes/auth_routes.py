# ============================================================
#  AUTH ROUTES — Register / Login / Logout / Profile
#  ENHANCED: Support redirect back to checkout after login
# ============================================================
from flask import Blueprint, request, jsonify, session
from models.user_model import db, User
from services.notification_service import send_welcome_email

auth_bp = Blueprint('auth', __name__)


# ── REGISTER ────────────────────────────────────────────────
@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """
    Register new user and auto-login
    
    Response includes redirect URL to support:
    - Regular registration → Home
    - Checkout registration → Back to checkout
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data received'}), 400

        required = ['firstName', 'lastName', 'email', 'phone', 'password']
        for field in required:
            if not data.get(field, '').strip():
                return jsonify({
                    'success': False,
                    'message': f'{field} is required'
                }), 400

        email = data['email'].lower().strip()
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({
                'success': False,
                'message': 'Email already registered. Please login.'
            }), 409

        # Validate passwords match
        if data.get('password') != data.get('confirmPassword'):
            return jsonify({
                'success': False,
                'message': 'Passwords do not match'
            }), 400

        # Validate password strength
        if len(data['password']) < 8:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 8 characters'
            }), 400

        # Create new user
        user = User(
            first_name=data['firstName'].strip(),
            last_name=data['lastName'].strip(),
            email=email,
            phone=data['phone'].strip(),
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        # Auto-login the user
        session.permanent = True
        session['user_id'] = user.id
        session['user_name'] = user.first_name
        session['user_email'] = user.email

        # Send welcome email
        send_welcome_email(user)

        print(f"[REGISTER] ✅ New user: {user.email}")

        return jsonify({
            'success': True,
            'message': f'Welcome {user.first_name}! Account created successfully.',
            'user': user.to_dict(),
            'redirect': '/checkout'  # Return to checkout after signup
        })

    except Exception as e:
        db.session.rollback()
        print(f"[REGISTER ERROR] {e}")
        return jsonify({
            'success': False,
            'message': 'Registration failed. Try again.'
        }), 500


# ── LOGIN ────────────────────────────────────────────────────
@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """
    Login existing user
    
    Response includes redirect URL to support:
    - Regular login → Home (or previous page)
    - Checkout login → Back to checkout
    - Profile login → Back to profile
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data received'}), 400

        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        remember = data.get('remember', False)

        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401

        # Set session
        session.permanent = bool(remember)
        session['user_id'] = user.id
        session['user_name'] = user.first_name
        session['user_email'] = user.email

        print(f"[LOGIN] ✅ User logged in: {user.email}")

        return jsonify({
            'success': True,
            'message': f'Welcome back, {user.first_name}!',
            'user': user.to_dict(),
            'redirect': '/checkout'  # Return to checkout after login
        })

    except Exception as e:
        print(f"[LOGIN ERROR] {e}")
        return jsonify({
            'success': False,
            'message': 'Login failed. Try again.'
        }), 500


# ── LOGOUT ───────────────────────────────────────────────────
@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user and clear session"""
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })


# ── GET CURRENT USER ─────────────────────────────────────────
@auth_bp.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """Get currently logged-in user details"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({
            'success': False,
            'logged_in': False,
            'message': 'Not logged in'
        }), 401
    
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return jsonify({
            'success': False,
            'logged_in': False,
            'message': 'User session invalid'
        }), 401
    
    return jsonify({
        'success': True,
        'logged_in': True,
        'user': user.to_dict()
    })


# ── CONTACT FORM ─────────────────────────────────────────────
@auth_bp.route('/api/contact', methods=['POST'])
def contact():
    """Handle contact form submissions"""
    try:
        data = request.get_json()
        from models.user_model import ContactMessage
        
        msg = ContactMessage(
            name=data.get('name', '').strip(),
            email=data.get('email', '').strip(),
            phone=data.get('phone', '').strip(),
            subject=data.get('subject', '').strip(),
            message=data.get('message', '').strip(),
        )
        db.session.add(msg)
        db.session.commit()
        
        print(f"[CONTACT] New message from: {msg.email}")
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully!'
        })
    except Exception as e:
        db.session.rollback()
        print(f"[CONTACT ERROR] {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
