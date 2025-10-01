from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from models import db, Post, Comment
from sqlalchemy.exc import IntegrityError

from utils.roles import role_required
from utils.validators import validate_comment_data

comments_bp = Blueprint('comments_bp', __name__)
@comments_bp.route('/posts/<int:post_id>/comments', methods=['GET'])

def get_post_comments(post_id):
    """
   Получение всех комментариев для конкретного поста
   """
    Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).all()
    return jsonify([comments.to_dict() for comments in comments])

@comments_bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@jwt_required()
@role_required('commentator', 'writer', 'admin')
def create_comment(post_id):
    """
    Создание нового комментария для поста
    Требуемые поля в теле запроса (JSON):
    - text: текст комментария
    """
    Post.query.get_or_404(post_id)

    data = request.get_json()

    # Валидируем данные
    is_valid, errors = validate_comment_data(data)
    if not is_valid:
        return jsonify({'errors': errors}), 400

    try:
        # Создаем новый комментарий
        new_comment = Comment(text=data['text'], post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()

        return jsonify(new_comment.to_dict()), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Database error'}), 500

@comments_bp.route('/comments/<int:comment_id>', methods=['GET'])
def get_comment(comment_id):
    """
    Получение комментария по ID
    """
    comment = Comment.query.get_or_404(comment_id)
    return jsonify(comment.to_dict())


@comments_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@role_required('admin')
@jwt_required()
def delete_comment(comment_id):
    """
    Удаление комментария
    """
    comment = Comment.query.get_or_404(comment_id)

    try:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'message': 'Comment deleted successfully'})

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Database error'}), 500