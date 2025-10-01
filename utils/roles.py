from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models import User

def role_required(*roles):
    def wrapper(fn):
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user or user.role not in roles:
                return jsonify({'error': 'Access denied'}), 403
            return fn(*args, **kwargs)
        decorator.__name__ = fn.__name__
        return decorator
    return wrapper
