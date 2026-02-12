from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cache = Cache()

def create_app(config_object=None):
    app = Flask(__name__)
    
    # 默认配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a5af302a0795ef80048887572854ef68')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['WTF_CSRF_CHECK_DEFAULT'] = False
    # JWT配置
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', '83a0c8f02d175f444a43013ba83fb3ca')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    app.config['JWT_TOKEN_LOCATION'] = ['headers']  # 从请求头获取token
    app.config['JWT_HEADER_NAME'] = 'Authorization'  # 请求头名称
    app.config['JWT_HEADER_TYPE'] = 'Bearer'        # token类型
    
    # Redis缓存配置
    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_HOST'] = os.getenv('REDIS_HOST', '127.0.0.1')
    app.config['CACHE_REDIS_PORT'] = int(os.getenv('REDIS_PORT', 6379))
    app.config['CACHE_REDIS_DB'] = int(os.getenv('REDIS_DB', 0))
    app.config['CACHE_REDIS_PASSWORD'] = os.getenv('REDIS_PASSWORD', 'jiong')
    app.config['CACHE_REDIS_URL'] = os.getenv('REDIS_URL', 'redis://:jiong@127.0.0.1:6379/6')
    app.config['CACHE_DEFAULT_TIMEOUT'] = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
    
    # Celery配置 - 全部使用新格式（大写，无CELERY_前缀）
    app.config['broker_url'] = os.getenv('CELERY_BROKER_URL', 'redis://:jiong@127.0.0.1:6379/7')
    app.config['result_backend'] = os.getenv('CELERY_RESULT_BACKEND', 'redis://:jiong@127.0.0.1:6379/8')
    app.config['timezone'] = 'Asia/Shanghai'
    app.config['enable_utc'] = False
    app.config['task_track_started'] = True
    app.config['task_time_limit'] = 30 * 60
    app.config['broker_connection_retry_on_startup'] = True
    app.config['beat_schedule'] = {}  # 注意：这里是 beat_schedule，不是 CELERY_BEAT_SCHEDULE
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cache.init_app(app)
    
    # 初始化Celery
    from app.utils.tasks import make_celery
    celery = make_celery(app)
    app.celery = celery
    
    # 注册蓝图
    from app.api.auth import auth_bp
    from app.api.posts import posts_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(posts_bp, url_prefix='/api/posts')
    
    # 注册定时任务
    from app.tasks.scheduled_tasks import setup_periodic_tasks
    setup_periodic_tasks(app.celery)
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': '资源未找到', 'code': 404}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': '服务器内部错误', 'code': 500}), 500
    
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({'error': '缺少认证令牌', 'code': 401}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return jsonify({'error': '无效的认证令牌', 'code': 401}), 401
    
    @jwt.expired_token_loader
    def expired_token_response(jwt_header, jwt_payload):
        return jsonify({'error': '认证令牌已过期', 'code': 401}), 401
    
    return app