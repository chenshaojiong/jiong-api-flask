from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app import db
from app.models.user import User
from app.schemas.user import RegisterForm, LoginForm
from app.utils.jwt_util import generate_tokens
from app.utils.decorators import validate_form
from app.utils.cache import ModelCache, clear_cache_by_prefix
from app.tasks.email_tasks import send_welcome_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@validate_form(RegisterForm)
def register(form):
    """用户注册"""
    user = User(
        username=form.username.data,
        email=form.email.data
    )
    user.password = form.password.data
    
    db.session.add(user)
    db.session.commit()
    
    # 生成令牌
    tokens = generate_tokens(user.id, user.username)
    
    # 异步发送欢迎邮件
    send_welcome_email.delay(user.id, user.email, user.username)
    
    return jsonify({
        'message': '注册成功',
        'code': 201,
        'data': {
            'user': user.to_dict(),
            **tokens
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
@validate_form(LoginForm)
def login(form):
    """用户登录"""
    user = User.query.filter_by(username=form.username.data).first()
    
    if not user or not user.check_password(form.password.data):
        return jsonify({'error': '用户名或密码错误', 'code': 401}), 401
    
    # 生成令牌
    tokens = generate_tokens(user.id, user.username)
    
    return jsonify({
        'message': '登录成功',
        'code': 200,
        'data': {
            'user': user.to_dict(),
            **tokens
        }
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': '用户不存在', 'code': 401}), 401
    
    access_token = create_access_token(
        identity=current_user_id,
        additional_claims={'username': user.username}
    )
    
    return jsonify({
        'message': '令牌刷新成功',
        'code': 200,
        'data': {
            'access_token': access_token,
            'token_type': 'Bearer'
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户注销（客户端需要删除token，服务端可选地将token加入黑名单）"""
    # 这里可以实现JWT黑名单功能
    return jsonify({
        'message': '注销成功',
        'code': 200
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    """获取当前用户信息"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': '用户不存在', 'code': 404}), 404
    
    return jsonify({
        'code': 200,
        'data': user.to_dict()
    }), 200