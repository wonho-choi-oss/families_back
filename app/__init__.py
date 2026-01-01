from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import config_by_name
from dotenv import load_dotenv
import redis
import os

load_dotenv()
db = SQLAlchemy()

# Redis 설정 (환경 변수 또는 기본값)
redis_client = redis.StrictRedis(
    host=os.environ.get('REDIS_HOST', 'localhost'),
    port=6379,
    db=0,
    decode_responses=True
)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    CORS(app)
    db.init_app(app)

    from .errors import register_error_handlers
    from .routes.auth_routes import auth_bp
    from .routes.family_routes import family_bp
    from .routes.gpt_routes import gpt_bp

    register_error_handlers(app)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(family_bp, url_prefix='/api/families')
    app.register_blueprint(gpt_bp, url_prefix='/api/gpt')

    with app.app_context():
        db.create_all()

    return app
