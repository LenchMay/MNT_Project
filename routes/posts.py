from flask import Blueprint, request, jsonify
from models import db, Post
from sqlalchemy.exc import IntegrityError
from utils.validators import validate_post_data
from flask_jwt_extended import jwt_required, get_jwt_identity

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/posts', methods=['GET'])
@jwt_required()
def get_posts():
    """
    Получение списка постов с пагинацией, фильтрацией и сортировкой
    Параметры запроса:
    - page: номер страницы (по умолчанию 1)
    - per_page: количество элементов на странице (по умолчанию 10)
    - title: фильтр по заголовку (опционально)
    - q: поисковый запрос (опционально)
    - sort: поле для сортировки (по умолчанию 'date_posted')
    - order: направление сортировки ('asc' или 'desc', по умолчанию 'desc')
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        query = Post.query

        title_filter = request.args.get('title')
        if title_filter:
            query = query.filter(Post.title.ilike('%' + title_filter + '%'))

        search_query = request.args.get('q')
        if search_query:
            query = query.filter(
                db.or_(
                    Post.title.ilike(f'%{search_query}%'),
                    Post.content.ilike(f'%{search_query}%')
                )
            )

        # Сортировка
        sort_by = request.args.get('sort', 'date_posted')
        sort_order = request.args.get('order', 'desc')

        # Проверяем, существует ли поле для сортировки в модели
        if hasattr(Post, sort_by):
            field = getattr(Post, sort_by)
            if sort_order == 'desc':
                query = query.order_by(db.desc(field))
            else:
                query = query.order_by(field)
        else:
            # Если поле не существует, используем сортировку по умолчанию
            query = query.order_by(db.desc(Post.date_posted))

        # Применяем пагинацию
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        posts = pagination.items

        # Формируем ответ
        return jsonify({
            'posts': [post.to_dict() for post in posts],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })


    except Exception as e:

        print("Ошибка в get_posts:", e)  # <-- чтобы увидеть проблему в консоли

        return jsonify({'error': 'Internal server error'}), 500


@posts_bp.route('/posts', methods=['POST'])
def create_post():
    """
    Создание нового поста
    Требуемые поля в теле запроса (JSON):
    - title: заголовок поста
    - content: содержимое поста
    """
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    # Валидируем данные
    is_valid, errors = validate_post_data(data)
    if not is_valid:
        return jsonify({'errors': errors}), 400

    try:
        # Создаем новый пост
        new_post = Post(
            title=data['title'],
            content=data['content'],
            category_id=data.get('category_id'),
            user_id=current_user_id
        )

        db.session.add(new_post)
        db.session.commit()

        # Возвращаем созданный пост
        return jsonify(new_post.to_dict()), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Database error'}), 500


@posts_bp.route('/posts/<int:post_id>', methods=['GET'])
@jwt_required()
def get_post(post_id):
    """
    Получение конкретного поста по ID
    """
    post = Post.query.get_or_404(post_id)
    return jsonify(post.to_dict())


@posts_bp.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Полное обновление поста
    """
    current_user_id = int(get_jwt_identity())
    post = Post.query.get_or_404(post_id)
    data = request.get_json()

    # Проверка прав доступа
    if post.user_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403
    data = request.get_json()
    # Валидируем данные
    is_valid, errors = validate_post_data(data)
    if not is_valid:
        return jsonify({'errors': errors}), 400

    try:
        # Обновляем пост
        post.title = data['title']
        post.content = data['content']
        db.session.commit()

        return jsonify(post.to_dict())

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Database error'}), 500


@posts_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    """
    Удаление поста
    """
    current_user_id = int(get_jwt_identity())
    post = Post.query.get_or_404(post_id)

    # Проверка прав доступа
    if post.user_id != current_user_id:
        return jsonify({'error': 'Access denied'}), 403

    try:
        db.session.delete(post)
        db.session.commit()
        return jsonify({'message': 'Post deleted successfully'})

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Database error'}), 500
