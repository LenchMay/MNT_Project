from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from models import db, Category, Post
from sqlalchemy.exc import IntegrityError

from utils.roles import role_required

categories_bp = Blueprint('categories', __name__)

# Получить все категории
@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([c.to_dict() for c in categories])

# Создать категорию
@categories_bp.route('/categories', methods=['POST'])
@jwt_required()
@role_required('writer', 'admin')
def create_category():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400

    new_category = Category(name=data['name'])
    try:
        db.session.add(new_category)
        db.session.commit()
        return jsonify(new_category.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Database error'}), 500

# Получить все посты конкретной категории
@categories_bp.route('/categories/<int:category_id>/posts', methods=['GET'])
def get_posts_by_category(category_id):
    category = Category.query.get_or_404(category_id)
    posts = Post.query.filter_by(category_id=category.id).all()
    return jsonify([p.to_dict() for p in posts])
