// ============================================================
//  CHECKOUT PAGE JS - ENHANCED WITH AUTHENTICATION
// ============================================================

// ── Load logged-in user details into form ──────────────────
async function prefillUserDetails() {
    try {
        const res = await fetch('/api/auth/me');
        const data = await res.json();
        if (data.success && data.logged_in && data.user) {
            const u = data.user;
            const set = (id, val) => { const el = document.getElementById(id); if (el && !el.value) el.value = val || ''; };
            set('fullName', u.full_name);
            set('phone', u.phone);
            set('email', u.email);
            
            let hidden = document.getElementById('_userEmail');
            if (!hidden) {
                hidden = document.createElement('input');
                hidden.type = 'hidden';
                hidden.id = '_userEmail';
                document.body.appendChild(hidden);
            }
            hidden.value = u.email;
        }
    } catch (e) {
        console.error('[checkout.js] Error prefilling user details:', e);
    }
}

// ── Check if user is logged in ───────────────────────────────
async function isUserLoggedIn() {
    try {
        const res = await fetch('/api/auth/me');
        const data = await res.json();
        return data.success && data.logged_in;
    } catch (e) {
        console.error('[checkout.js] Error checking login status:', e);
        return false;
    }
}

// ── Show authentication modal ────────────────────────────────
function showAuthenticationModal() {
    // Remove existing modal if any
    const existing = document.getElementById('authModal');
    if (existing) existing.remove();

    const modal = document.createElement('div');
    modal.id = 'authModal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;

    modal.innerHTML = `
    <div style="background: white; border-radius: 16px; padding: 32px; max-width: 400px; width: 90%; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
        <div style="text-align: center; margin-bottom: 24px;">
            <h2 style="margin: 0 0 12px 0; font-size: 24px; color: #1F2937;">Secure Checkout</h2>
            <p style="margin: 0; color: #6B7280; font-size: 14px;">Please create an account or login to continue your order.</p>
        </div>

        <div style="margin-bottom: 24px;">
            <p style="margin: 0 0 12px 0; color: #6B7280; font-size: 13px; text-align: center;">
                ✅ Faster checkout next time<br>
                ✅ Track your orders<br>
                ✅ Save delivery addresses<br>
                ✅ Exclusive offers
            </p>
        </div>

        <div style="display: flex; gap: 12px; margin-bottom: 16px;">
            <button onclick="redirectToLogin()" style="
                flex: 1;
                padding: 12px 16px;
                background: #E8471A;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.2s;
            " onmouseover="this.style.background='#D63A10'" onmouseout="this.style.background='#E8471A'">
                Login
            </button>
            <button onclick="redirectToSignup()" style="
                flex: 1;
                padding: 12px 16px;
                background: #F3F4F6;
                color: #1F2937;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.2s;
            " onmouseover="this.style.background='#E5E7EB'" onmouseout="this.style.background='#F3F4F6'">
                Sign Up
            </button>
        </div>

        <button onclick="closeAuthModal()" style="
            width: 100%;
            padding: 12px 16px;
            background: transparent;
            color: #6B7280;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            transition: background 0.2s;
        " onmouseover="this.style.background='#F9FAFB'" onmouseout="this.style.background='transparent'">
            Continue as Guest
        </button>

        <p style="margin: 16px 0 0 0; font-size: 12px; color: #9CA3AF; text-align: center;">
            Your cart will be saved. You can login anytime.
        </p>
    </div>`;

    document.body.appendChild(modal);
}

// ── Close auth modal ─────────────────────────────────────────
function closeAuthModal() {
    const modal = document.getElementById('authModal');
    if (modal) {
        modal.style.opacity = '0';
        modal.style.transition = 'opacity 0.2s ease';
        setTimeout(() => modal.remove(), 200);
    }
}

// ── Redirect to login with cart preservation ─────────────────
function redirectToLogin() {
    // Cart is already saved in localStorage
    sessionStorage.setItem('returnAfterLogin', '/checkout');
    window.location.href = '/login';
}

// ── Redirect to signup with cart preservation ────────────────
function redirectToSignup() {
    // Cart is already saved in localStorage
    sessionStorage.setItem('returnAfterLogin', '/checkout');
    window.location.href = '/register';
}

// ── Initialize checkout ──────────────────────────────────────
async function initCheckout() {
    const checkoutItems = document.getElementById('checkoutItems');
    if (!checkoutItems) return;
    
    const cart = Storage.getCart();
    if (cart.length === 0) {
        window.location.href = '/cart';
        return;
    }

    // Build checkout items display
    const itemsHTML = cart.map(item => `
        <div class="checkout-item">
            <span class="checkout-item-name">${item.emoji} ${item.name}${item.weight ? ' (' + item.weight + ')' : ''}</span>
            <span class="checkout-item-qty">×${item.qty}</span>
            <span class="checkout-item-price">₹${item.price * item.qty}</span>
        </div>`).join('');

    checkoutItems.innerHTML = itemsHTML;

    const sub = Storage.getTotal();
    const total = sub + 40; // delivery charge

    const subEl = document.getElementById('coSubtotal');
    const totalEl = document.getElementById('coTotal');
    
    if (subEl) subEl.textContent = `₹${sub}`;
    if (totalEl) totalEl.textContent = `₹${total}`;
}

// ── Apply coupon code ────────────────────────────────────────
function applyCheckoutCoupon() {
    const code = document.getElementById('coCoupon')?.value?.toUpperCase();
    const msg = document.getElementById('coCouponMsg');
    
    if (code === 'FIRST10' || code === 'FIRST20') {
        const pct = code === 'FIRST10' ? 0.1 : 0.2;
        const discount = Math.round(Storage.getTotal() * pct);
        
        if (msg) {
            msg.textContent = `✅ ₹${discount} discount applied!`;
            msg.className = 'coupon-msg success';
        }
        
        const totalEl = document.getElementById('coTotal');
        if (totalEl) {
            totalEl.textContent = `₹${Storage.getTotal() + 40 - discount}`;
        }
    } else {
        if (msg) {
            msg.textContent = '❌ Invalid coupon';
            msg.className = 'coupon-msg error';
        }
    }
}

// ── Place order with authentication check ────────────────────
async function placeOrder() {
    // Check if user is logged in
    const loggedIn = await isUserLoggedIn();
    
    if (!loggedIn) {
        // Show authentication modal
        showAuthenticationModal();
        return;
    }

    // User is logged in, proceed with order
    await proceedWithOrder();
}

// ── Actual order placement ───────────────────────────────────
async function proceedWithOrder() {
    const fields = {
        fullName: document.getElementById('fullName')?.value?.trim(),
        phone: document.getElementById('phone')?.value?.trim(),
        email: (document.getElementById('email')?.value?.trim()) ||
               (document.getElementById('_userEmail')?.value?.trim()) || '',
        address1: document.getElementById('address1')?.value?.trim(),
        address2: document.getElementById('address2')?.value?.trim() || '',
        city: document.getElementById('city')?.value?.trim(),
        pincode: document.getElementById('pincode')?.value?.trim(),
        instructions: document.getElementById('instructions')?.value?.trim() || '',
    };

    // Validation
    if (!fields.fullName) {
        showFormError('Please enter your full name!');
        return;
    }
    if (!fields.phone || fields.phone.length < 10) {
        showFormError('Please enter a valid phone number!');
        return;
    }
    if (!fields.email || !fields.email.includes('@')) {
        showFormError('Please enter your email address for order confirmation!');
        return;
    }
    if (!fields.address1) {
        showFormError('Please enter your delivery address!');
        return;
    }
    if (!fields.city) {
        showFormError('Please enter your city!');
        return;
    }
    if (!fields.pincode || fields.pincode.length < 5) {
        showFormError('Please enter a valid PIN code!');
        return;
    }

    const paymentMethod = 'cod'; // Cash on Delivery only
    const cart = Storage.getCart();
    
    if (cart.length === 0) {
        window.location.href = '/cart';
        return;
    }

    const btn = document.getElementById('placeOrderBtn');
    btn.innerHTML = '<span class="btn-spinner"></span> Placing Order...';
    btn.disabled = true;
    clearFormError();

    try {
        const response = await fetch('/api/order/place', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ...fields,
                paymentMethod,
                items: cart.map(i => ({
                    id: i.id,
                    name: i.name,
                    emoji: i.emoji || '🍱',
                    weight: i.weight || '',
                    qty: i.qty,
                    price: i.price
                }))
            })
        });

        if (!response.ok) {
            if (response.status === 401) {
                // User session expired
                showFormError('Your session has expired. Please login again.');
                setTimeout(() => redirectToLogin(), 2000);
                return;
            }
            showFormError('Server error. Please refresh and try again.');
            btn.innerHTML = 'Place Order 🎉';
            btn.disabled = false;
            return;
        }

        const result = await response.json();
        if (result.success) {
            Storage.clearCart();
            sessionStorage.setItem('lastOrderId', result.order_id);
            sessionStorage.setItem('lastOrderTotal', result.grand_total);
            sessionStorage.setItem('lastPaymentMethod', paymentMethod);
            window.location.href = '/order-success';
        } else {
            showFormError(result.message || 'Order could not be placed. Please try again.');
            btn.innerHTML = 'Place Order 🎉';
            btn.disabled = false;
        }
    } catch (err) {
        console.error('[checkout.js] Order error:', err);
        showFormError('Connection error! Check your internet and try again.');
        btn.innerHTML = 'Place Order 🎉';
        btn.disabled = false;
    }
}

// ── Form error display ───────────────────────────────────────
function showFormError(msg) {
    clearFormError();
    const el = document.createElement('div');
    el.id = 'formError';
    el.style.cssText = 'background:#FEE2E2;color:#DC2626;padding:14px 20px;border-radius:10px;margin-bottom:16px;font-size:14px;font-weight:500;';
    el.textContent = '⚠️ ' + msg;
    const btn = document.getElementById('placeOrderBtn');
    btn?.parentNode?.insertBefore(el, btn);
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function clearFormError() {
    document.getElementById('formError')?.remove();
}

// ── On page load ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initCheckout();
    prefillUserDetails();
});
