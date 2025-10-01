from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token

db = SQLAlchemy()

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now())

    comments = db.relationship('Comment', backref='post', lazy=True)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey('category.id', name='fk_post_category'),
        nullable=False
    )
    category = db.relationship('Category', backref='posts', lazy=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id', name='fk_post_user'),
        nullable=False
    )

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'date_posted': self.date_posted.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'comments_count': len(self.comments),
            'category_id': self.category_id,
            'category': self.category.name,
            'user_id': self.user_id,
            'author': self.author.username if self.author else None
        }

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    date_published = db.Column(db.DateTime, server_default=db.func.now())
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'date_published': str(self.date_published) if hasattr(self, 'date_published') else None,
            'post_id': self.post_id
        }

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    is_active = db.Column(db.Boolean, default=True)

    posts = db.relationship('Post', backref='author', lazy=True)
    role = db.Column(db.String(20), default='commentator')

    def set_password(self, password):
        """Установка хэшированного пароля"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Проверка пароля"""
        return check_password_hash(self.password_hash, password)

    def generate_tokens(self):
        """Генерация access и refresh токенов"""
        return {
            'access_token': create_access_token(identity=str(self.id)),
            'refresh_token': create_refresh_token(identity=str(self.id))
        }

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'role': self.role
        }
