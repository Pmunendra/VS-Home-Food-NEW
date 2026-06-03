# ============================================================
#  PRODUCT MODEL — DB-backed products with variants
# ============================================================
from models.user_model import db
from datetime import datetime
import json


class Product(db.Model):
    __tablename__ = 'products'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    category    = db.Column(db.String(100), default='general')
    emoji       = db.Column(db.String(10), default='🍱')
    image_file  = db.Column(db.String(255), default='')   # filename in static/images/products/
    price       = db.Column(db.Float, nullable=False, default=0.0)   # base price
    quantity    = db.Column(db.Integer, default=0)
    status      = db.Column(db.String(20), default='in_stock')       # 'in_stock' | 'out_of_stock'
    badge       = db.Column(db.String(50), default='')
    is_veg      = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Variants stored as JSON: [{"label":"250g","price":120}, ...]
    variants_json = db.Column(db.Text, default='[]')

    def set_variants(self, variants_list):
        """variants_list = [{'label': '250g', 'price': 120}, ...]"""
        self.variants_json = json.dumps(variants_list)

    def get_variants(self):
        try:
            return json.loads(self.variants_json) if self.variants_json else []
        except Exception:
            return []

    def auto_status(self):
        """Auto-set Out of Stock when quantity hits 0."""
        if self.quantity <= 0:
            self.status = 'out_of_stock'

    def to_dict(self):
        variants = self.get_variants()
        return {
            'id':          self.id,
            'name':        self.name,
            'description': self.description,
            'category':    self.category,
            'emoji':       self.emoji,
            'image_file':  self.image_file,
            'image_url':   f'/static/images/products/{self.image_file}' if self.image_file else '',
            'price':       variants[0]['price'] if variants else self.price,
            'quantity':    self.quantity,
            'status':      self.status,
            'in_stock':    self.status == 'in_stock',
            'badge':       self.badge,
            'is_veg':      self.is_veg,
            'variants':    variants,
            'created_at':  self.created_at.isoformat(),
        }
