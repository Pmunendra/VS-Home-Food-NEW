import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'amma-vanta-secret-key-change-me'
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

    # ── SQLite DB ─────────────────────────────────────────────
    DB_FOLDER = os.path.join(BASE_DIR, 'database')
    os.makedirs(DB_FOLDER, exist_ok=True)
    SQLALCHEMY_DATABASE_URI        = os.environ.get('DATABASE_URL') or \
                                     'sqlite:///' + os.path.join(DB_FOLDER, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Session / Cookie ─────────────────────────────────────
    SESSION_COOKIE_HTTPONLY  = True
    SESSION_COOKIE_SAMESITE  = 'Lax'
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 30   # 30 days

    # ── Gmail SMTP ────────────────────────────────────────────
    MAIL_SERVER         = 'smtp.gmail.com'
    MAIL_PORT           = 587
    MAIL_USE_TLS        = True
    MAIL_USE_SSL        = False
    MAIL_USERNAME       = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD       = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME', '')
    MAIL_SUPPRESS_SEND  = False

    # ── Admin ─────────────────────────────────────────────────
    ADMIN_EMAIL      = os.environ.get('ADMIN_EMAIL', 'owner@ammavanta.com')
    ADMIN_WHATSAPP   = os.environ.get('ADMIN_WHATSAPP', '+919876543210')
    ADMIN_PASSWORD   = os.environ.get('ADMIN_PASSWORD', 'admin123')   # change in .env!

    # ── Twilio WhatsApp ───────────────────────────────────────
    TWILIO_ACCOUNT_SID   = os.environ.get('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN    = os.environ.get('TWILIO_AUTH_TOKEN', '')
    TWILIO_WHATSAPP_FROM = 'whatsapp:+14155238886'
