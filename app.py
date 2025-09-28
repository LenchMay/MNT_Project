from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import Config
from models import db
from routes.posts import posts_bp
from routes.comments import comments_bp
from routes.categories import categories_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    jwt = JWTManager(app)

    db.init_app(app)

    migrate = Migrate(app, db)

    app.register_blueprint(posts_bp, url_prefix='/api')
    app.register_blueprint(comments_bp, url_prefix='/api')
    app.register_blueprint(categories_bp, url_prefix='/api')

    # CLI команды для миграций
    @app.cli.command('db-init')
    def db_init():
        import os
        if not os.path.exists('migrations'):
            os.system('flask db init')
            print("Миграции инициализированы")

    # JWT колбэки
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'token has expired'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'invalid token'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Missing authorization token'}), 401

    # Обработчики ошибок
    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=8088)