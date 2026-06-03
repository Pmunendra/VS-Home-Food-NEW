# 🍱 Amma Vanta — Homemade Food Delivery

> Authentic Telugu homemade food delivered fresh — built with Flask + SQLAlchemy

---

## ✨ Features

- **Full Auth System** — Register, Login, Logout with Werkzeug password hashing
- **Session Management** — Remember me, persistent sessions, server-side user injection
- **Navbar User Dropdown** — Hi, USERNAME with My Orders / Profile / Logout
- **Complete Order Flow** — Cart → Checkout → Order saved to DB → Success page
- **Email Notifications** — Customer confirmation + Admin alert via Gmail SMTP
- **WhatsApp Notifications** — Admin WhatsApp alert via Twilio (optional)
- **Admin Dashboard** — Stats, all orders, update status, search/filter, user list
- **Error Pages** — Custom 404 and 500 pages
- **SQLite by default** — Zero config needed; MySQL supported via env var

---

## 🚀 Quick Setup

### 1. Clone / Unzip the project

```bash
cd Food_Delivery_Project
```

### 2. Create virtual environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your values
```

### 5. Run the app

```bash
python app.py
```

Visit: http://localhost:5000

---

## 📧 Email Setup (Gmail)

1. Go to [myaccount.google.com](https://myaccount.google.com) → Security
2. Enable **2-Step Verification**
3. Go to **App passwords** → Select app: Mail → Generate
4. Copy the 16-digit code into `.env` as `MAIL_PASSWORD`
5. Set `MAIL_USERNAME` to your Gmail address

---

## 📱 WhatsApp Setup (Twilio — Optional)

1. Create free account at [twilio.com](https://twilio.com)
2. Go to Console → copy `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`
3. Paste into `.env`
4. Send "join <sandbox-word>" to the Twilio WhatsApp sandbox number

---

## 🗄️ Database Setup

**SQLite (default)** — Works automatically. DB file is created at `database/database.db`.

**MySQL** — Install PyMySQL and set in `.env`:
```
pip install pymysql
DATABASE_URL=mysql+pymysql://user:password@localhost/ammavanta_db
```

---

## 🔐 Admin Dashboard

1. Visit: http://localhost:5000/admin
2. Enter the `ADMIN_PASSWORD` from your `.env` (default: `admin123`)
3. Change this immediately in production!

---

## 📁 Project Structure

```
amma_vanta/
├── app.py                    # Main Flask app
├── config.py                 # Config class
├── requirements.txt
├── .env.example
├── models/
│   ├── user_model.py         # User, ContactMessage
│   └── order_model.py        # Order
├── routes/
│   ├── auth_routes.py        # Register, Login, Logout, /api/auth/*
│   ├── order_routes.py       # Place order, get orders, stats
│   ├── product_routes.py     # Product catalogue API
│   └── admin_routes.py       # Admin dashboard routes
├── services/
│   └── notification_service.py  # Email + WhatsApp
├── templates/
│   ├── base.html
│   ├── index.html, menu.html, cart.html, checkout.html
│   ├── login.html, register.html
│   ├── profile.html, my-orders.html
│   ├── order-success.html
│   ├── components/           # navbar, footer, sidebar-cart
│   ├── admin/                # dashboard, orders, users, login
│   └── errors/               # 404, 500
└── static/
    ├── css/                  # style, navbar, hero, products, checkout...
    └── js/                   # main, cart, checkout, storage, search...
```

---

## 🛡️ Security Notes

- Passwords hashed with `werkzeug.security`
- Sessions are HTTP-only cookies
- Admin protected by password + session check
- SQL injection prevented via SQLAlchemy ORM
- Change `SECRET_KEY` and `ADMIN_PASSWORD` before deploying!
