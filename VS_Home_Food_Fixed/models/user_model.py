from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id         = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name  = db.Column(db.String(80), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    phone      = db.Column(db.String(20), nullable=False)
    password   = db.Column(db.String(256), nullable=False)
    is_admin   = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders     = db.relationship('Order', backref='user', lazy=True)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def to_dict(self):
        return {
            'id':         self.id,
            'first_name': self.first_name,
            'last_name':  self.last_name,
            'full_name':  f"{self.first_name} {self.last_name}",
            'email':      self.email,
            'phone':      self.phone,
            'is_admin':   self.is_admin,
            'created_at': self.created_at.isoformat()
        }


class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(120), nullable=False)
    email      = db.Column(db.String(120), nullable=False)
    phone      = db.Column(db.String(20), default='')
    subject    = db.Column(db.String(255), default='')
    message    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
