# ============================================================
#  NOTIFICATION SERVICE
# ============================================================
from flask import current_app, render_template_string
from flask_mail import Mail, Message

mail = Mail()

# ── EMAIL TEMPLATES ──────────────────────────────────────────

WELCOME_TEMPLATE = """
<!DOCTYPE html><html><head><style>
  body{font-family:'Segoe UI',sans-serif;background:#FDF6EE;margin:0;padding:0}
  .w{max-width:600px;margin:40px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.1)}
  .h{background:linear-gradient(135deg,#E8471A,#FF6B35);padding:40px;text-align:center;color:#fff}
  .b{padding:32px}.hl{background:#FDF6EE;border-left:4px solid #E8471A;padding:16px 20px;border-radius:0 12px 12px 0;margin:24px 0}
  .btn{display:inline-block;background:#E8471A;color:#fff;padding:14px 32px;border-radius:50px;text-decoration:none;font-weight:700}
  .f{background:#1A1A1A;padding:24px;text-align:center;color:#888;font-size:13px}.f a{color:#E8471A}
</style></head><body>
<div class="w">
  <div class="h"><div style="font-size:52px;margin-bottom:12px">🍱</div><h1 style="margin:0">Welcome to Amma Vanta! 🎉</h1></div>
  <div class="b">
    <p style="font-size:18px">Hi <strong>{{ first_name }}</strong>,</p>
    <p style="color:#555;line-height:1.8">Amma Vanta Family లో join అయినందుకు చాలా సంతోషం! 🙏</p>
    <div class="hl">
      <strong>📋 Your Account:</strong><br>
      <span style="color:#555;font-size:14px;line-height:2">
        👤 Name: <strong>{{ full_name }}</strong><br>
        📧 Email: <strong>{{ email }}</strong><br>
        📞 Phone: <strong>{{ phone }}</strong>
      </span>
    </div>
    <div style="text-align:center"><a class="btn" href="#">Order Now →</a></div>
  </div>
  <div class="f">© 2024 Amma Vanta | Made with ❤️ in Hyderabad</div>
</div></body></html>
"""

CUSTOMER_ORDER_TEMPLATE = """
<!DOCTYPE html><html><head><style>
  body{font-family:'Segoe UI',sans-serif;background:#FDF6EE;margin:0;padding:0}
  .w{max-width:600px;margin:40px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.1)}
  .h{background:linear-gradient(135deg,#E8471A,#FF6B35);padding:40px;text-align:center;color:#fff}
  .b{padding:32px}
  .ob{background:#FDF6EE;border-radius:12px;padding:24px;margin-bottom:24px}
  .ob h3{margin:0 0 16px;color:#E8471A;font-size:14px;text-transform:uppercase;letter-spacing:1px}
  .ir{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #F5E8D6;font-size:15px}
  .ir:last-child{border:none}
  .tr{display:flex;justify-content:space-between;padding:14px 0 0;font-size:18px;font-weight:700;color:#E8471A}
  .ab{background:#f9f9f9;border-radius:12px;padding:20px;margin-bottom:24px;font-size:14px;color:#555;line-height:1.8}
  .badge{display:inline-block;background:#22C55E;color:#fff;padding:6px 18px;border-radius:50px;font-size:13px;font-weight:700}
  .f{background:#1A1A1A;padding:24px;text-align:center;color:#888;font-size:13px}.f a{color:#E8471A}
  .dv{height:1px;background:#F5E8D6;margin:12px 0}
</style></head><body>
<div class="w">
  <div class="h">
    <div style="font-size:48px;margin-bottom:12px">🍱</div>
    <h1 style="margin:0">Order Confirmed! 🎉</h1>
    <p style="opacity:.9;margin:8px 0 0">Thank you for ordering from Amma Vanta</p>
  </div>
  <div class="b">
    <p style="font-size:18px">Hi <strong>{{ customer_name }}</strong>,</p>
    <p style="color:#555;margin-bottom:24px">మీ order successfully place అయింది! మా kitchen prepare చేస్తోంది. 💛</p>
    <div class="ob">
      <h3>🛒 Order #{{ order_id }}</h3>
      {% for item in items %}
      <div class="ir">
        <span>{{ item.emoji }} {{ item.name }}{% if item.weight %} — <strong>{{ item.weight }}</strong>{% endif %} × {{ item.qty }}</span>
        <span><strong>₹{{ item.total }}</strong></span>
      </div>
      {% endfor %}
      <div class="dv"></div>
      <div class="ir"><span>Delivery Charge</span><span>₹40</span></div>
      <div class="tr"><span>Total Paid</span><span>₹{{ grand_total }}</span></div>
    </div>
    <div class="ab">
      <strong>📍 Delivery Address</strong><br>
      {{ address.name }}<br>
      {{ address.line1 }}{% if address.line2 %}, {{ address.line2 }}{% endif %}<br>
      {{ address.city }} — {{ address.pincode }}<br>
      📞 {{ address.phone }}
    </div>
    <div style="text-align:center;margin-bottom:24px">
      <span class="badge">⏱️ Estimated Delivery: 45–60 mins</span>
    </div>
    <p style="color:#555;font-size:14px;line-height:1.7">
      Questions ఉంటే WhatsApp: <strong>{{ admin_whatsapp }}</strong>
    </p>
  </div>
  <div class="f">© 2024 Amma Vanta | Made with ❤️ in Hyderabad</div>
</div></body></html>
"""

ADMIN_ORDER_TEMPLATE = """
<!DOCTYPE html><html><head><style>
  body{font-family:'Segoe UI',sans-serif;background:#f4f4f4;margin:0;padding:0}
  .w{max-width:600px;margin:40px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.1)}
  .h{background:#1A1A1A;padding:32px;text-align:center;color:#fff}
  .al{background:#E8471A;color:#fff;padding:8px 20px;border-radius:50px;font-size:13px;font-weight:700;display:inline-block;margin-bottom:12px}
  .b{padding:32px}
  .gr{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px}
  .cd{background:#FDF6EE;border-radius:10px;padding:16px}
  .cd label{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#E8471A;font-weight:700;display:block;margin-bottom:6px}
  .cd span{font-size:15px;font-weight:600;color:#1A1A1A}
  table{width:100%;border-collapse:collapse;margin-bottom:24px}
  th{background:#1A1A1A;color:#fff;padding:10px 14px;text-align:left;font-size:13px}
  td{padding:10px 14px;border-bottom:1px solid #f0f0f0;font-size:14px}
  tr:last-child td{border:none;font-weight:700;color:#E8471A;font-size:16px}
</style></head><body>
<div class="w">
  <div class="h">
    <div class="al">🔔 NEW ORDER RECEIVED</div>
    <h2 style="margin:0;color:#fff">Order #{{ order_id }}</h2>
    <p style="color:#888;margin:8px 0 0;font-size:14px">{{ order_time }}</p>
  </div>
  <div class="b">
    <div class="gr">
      <div class="cd"><label>👤 Customer</label><span>{{ address.name }}</span></div>
      <div class="cd"><label>📞 Phone</label><span>{{ address.phone }}</span></div>
      <div class="cd"><label>📧 Email</label><span>{{ customer_email }}</span></div>
      <div class="cd"><label>💳 Payment</label><span>{{ payment_method }}</span></div>
      <div class="cd"><label>💰 Total</label><span style="color:#E8471A">₹{{ grand_total }}</span></div>
      <div class="cd"><label>📦 Items</label><span>{{ items|length }} item(s)</span></div>
    </div>
    <p style="font-size:13px;color:#555;margin-bottom:16px">
      <strong>📍 Delivery Address:</strong><br>
      {{ address.line1 }}{% if address.line2 %}, {{ address.line2 }}{% endif %},
      {{ address.city }} — {{ address.pincode }}
    </p>
    <table>
      <thead><tr><th>Item</th><th>Qty</th><th>Amount</th></tr></thead>
      <tbody>
        {% for item in items %}
        <tr>
          <td>{{ item.emoji }} {{ item.name }}{% if item.weight %} — <strong>{{ item.weight }}</strong>{% endif %}</td>
          <td>× {{ item.qty }}</td>
          <td>₹{{ item.total }}</td>
        </tr>
        {% endfor %}
        <tr><td colspan="2">Grand Total</td><td>₹{{ grand_total }}</td></tr>
      </tbody>
    </table>
    {% if instructions %}
    <p style="background:#FFF3CD;padding:12px;border-radius:8px;font-size:14px">
      📝 <strong>Note:</strong> {{ instructions }}
    </p>
    {% endif %}
  </div>
</div></body></html>
"""

# ── HELPERS ──────────────────────────────────────────────────

def _mail_configured():
    """Check if MAIL_USERNAME is set in config."""
    try:
        username = current_app.config.get('MAIL_USERNAME', '').strip()
        if not username:
            print("[EMAIL] ⚠️  MAIL_USERNAME not set in .env — emails will be skipped.")
            print("[EMAIL]    → .env file open చేసి MAIL_USERNAME మరియు MAIL_PASSWORD fill చేయండి.")
            return False
        return True
    except Exception:
        return False

# ── WELCOME EMAIL ────────────────────────────────────────────
def send_welcome_email(user):
    """
    Send welcome email after successful registration.
    Runs inside Flask app context (called from auth_routes).
    """
    try:
        if not _mail_configured():
            return False

        html = render_template_string(
            WELCOME_TEMPLATE,
            first_name=user.first_name,
            full_name=f"{user.first_name} {user.last_name}",
            email=user.email,
            phone=user.phone,
        )
        msg = Message(
            subject="🎉 Welcome to Amma Vanta!",
            recipients=[user.email],
            html=html,
        )
        mail.send(msg)
        print(f"[EMAIL] ✅ Welcome email sent → {user.email}")
        return True

    except Exception as e:
        print(f"[EMAIL] ❌ Welcome email FAILED: {e}")
        print("[EMAIL]    Hint: Gmail App Password correct గా set చేశారా? .env చెక్ చేయండి.")
        return False


# ── CUSTOMER ORDER EMAIL ─────────────────────────────────────
def send_customer_email(order_data):
    try:
        if not _mail_configured():
            return False

        customer_email = order_data.get('customer_email', '').strip()
        if not customer_email:
            print("[EMAIL] ⚠️  customer_email missing — skipping customer order email")
            return False

        html = render_template_string(
            CUSTOMER_ORDER_TEMPLATE,
            customer_name=order_data['address']['name'],
            order_id=order_data['order_id'],
            items=order_data['items'],
            address=order_data['address'],
            grand_total=order_data['grand_total'],
            admin_whatsapp=current_app.config.get('ADMIN_WHATSAPP', ''),
        )
        msg = Message(
            subject=f"✅ Order Confirmed #{order_data['order_id']} — Amma Vanta",
            recipients=[customer_email],
            html=html,
        )
        mail.send(msg)
        print(f"[EMAIL] ✅ Order confirm sent → {customer_email}")
        return True

    except Exception as e:
        print(f"[EMAIL] ❌ Customer order email FAILED: {e}")
        return False


# ── ADMIN EMAIL ──────────────────────────────────────────────
def send_admin_email(order_data):
    try:
        if not _mail_configured():
            return False

        admin_email = current_app.config.get('ADMIN_EMAIL', '').strip()
        if not admin_email:
            print("[EMAIL] ⚠️  ADMIN_EMAIL not set — skipping admin alert")
            return False

        from datetime import datetime
        html = render_template_string(
            ADMIN_ORDER_TEMPLATE,
            order_id=order_data['order_id'],
            order_time=datetime.now().strftime('%d %b %Y, %I:%M %p'),
            items=order_data['items'],
            address=order_data['address'],
            customer_email=order_data['customer_email'],
            payment_method=order_data['payment_method'],
            grand_total=order_data['grand_total'],
            instructions=order_data.get('instructions', ''),
        )
        msg = Message(
            subject=f"🔔 New Order #{order_data['order_id']} — ₹{order_data['grand_total']}",
            recipients=[admin_email],
            html=html,
        )
        mail.send(msg)
        print(f"[EMAIL] ✅ Admin alert sent → {admin_email}")
        return True

    except Exception as e:
        print(f"[EMAIL] ❌ Admin email FAILED: {e}")
        return False


# ── ADMIN WHATSAPP ───────────────────────────────────────────
def send_admin_whatsapp(order_data):
    try:
        sid   = current_app.config.get('TWILIO_ACCOUNT_SID', '').strip()
        token = current_app.config.get('TWILIO_AUTH_TOKEN', '').strip()

        if not sid or not token or not sid.startswith('AC') or len(sid) < 30:
            print("[WHATSAPP] Twilio credentials not set — skipping WhatsApp")
            return False

        from twilio.rest import Client
        from datetime import datetime

        client     = Client(sid, token)
        items_text = "\n".join([
            f"  • {i['emoji']} {i['name']} x{i['qty']} = ₹{i['total']}"
            for i in order_data['items']
        ])
        msg = (
            f"🔔 *NEW ORDER — Amma Vanta*\n\n"
            f"📦 *Order ID:* #{order_data['order_id']}\n"
            f"💰 *Total:* ₹{order_data['grand_total']}\n"
            f"💳 *Payment:* {order_data['payment_method']}\n\n"
            f"👤 *Customer:*\n"
            f"Name: {order_data['address']['name']}\n"
            f"Phone: {order_data['address']['phone']}\n"
            f"Email: {order_data['customer_email']}\n"
            f"Address: {order_data['address']['line1']}, "
            f"{order_data['address']['city']} - {order_data['address']['pincode']}\n\n"
            f"🛒 *Items:*\n{items_text}\n\n"
            f"⏰ {datetime.now().strftime('%d %b %Y, %I:%M %p')}"
        )
        client.messages.create(
            from_=current_app.config['TWILIO_WHATSAPP_FROM'],
            to=f"whatsapp:{current_app.config['ADMIN_WHATSAPP']}",
            body=msg,
        )
        print("[WHATSAPP] ✅ Admin WhatsApp sent")
        return True

    except Exception as e:
        print(f"[WHATSAPP] ❌ FAILED: {e}")
        return False


# ── MASTER NOTIFY ────────────────────────────────────────────
def notify_order_placed(order_data):
    results = {
        'customer_email': send_customer_email(order_data),
        'admin_email':    send_admin_email(order_data),
        'admin_whatsapp': send_admin_whatsapp(order_data),
    }
    print(f"[NOTIFY] Final results: {results}")
    return results
