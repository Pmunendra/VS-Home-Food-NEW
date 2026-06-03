from models.user_model import db
from datetime import datetime
import json

class Order(db.Model):
    __tablename__ = 'orders'

    id             = db.Column(db.Integer, primary_key=True)
    order_id       = db.Column(db.String(20), unique=True, nullable=False)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_name  = db.Column(db.String(160), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    address_line1  = db.Column(db.String(255), nullable=False)
    address_line2  = db.Column(db.String(255), default='')
    city           = db.Column(db.String(100), nullable=False)
    pincode        = db.Column(db.String(10), nullable=False)
    items_json     = db.Column(db.Text, nullable=False)   # JSON string
    payment_method = db.Column(db.String(50), default='UPI')
    grand_total    = db.Column(db.Float, nullable=False)
    instructions   = db.Column(db.Text, default='')
    status         = db.Column(db.String(30), default='pending')
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    def set_items(self, items_list):
        self.items_json = json.dumps(items_list)

    def get_items(self):
        return json.loads(self.items_json) if self.items_json else []

    def to_dict(self):
        return {
            'order_id': self.order_id,
            'customer': self.customer_name,
            'phone': self.customer_phone,
            'email': self.customer_email,
            'address': {
                'name': self.customer_name,
                'phone': self.customer_phone,
                'line1': self.address_line1,
                'line2': self.address_line2,
                'city': self.city,
                'pincode': self.pincode,
            },
            'items': self.get_items(),
            'payment_method': self.payment_method,
            'grand_total': self.grand_total,
            'instructions': self.instructions,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
        }
