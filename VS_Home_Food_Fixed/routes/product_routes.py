# ============================================================
#  PRODUCT ROUTES — DB-backed product API
# ============================================================
from flask import Blueprint, jsonify, request
from models.product_model import Product

product_bp = Blueprint('products', __name__)


@product_bp.route('/api/products', methods=['GET'])
def get_products():
    cat = request.args.get('category', '').strip()
    q   = Product.query
    if cat:
        q = q.filter_by(category=cat)
    products = q.order_by(Product.created_at.desc()).all()
    return jsonify({'products': [p.to_dict() for p in products], 'success': True})


@product_bp.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    return jsonify({'success': True, 'product': product.to_dict()})
