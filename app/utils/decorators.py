from functools import wraps
import os
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"Authorization Header: {request.headers.get('Authorization', 'None')}")
        print(f'JWT_SECRET_KEY: {os.getenv("JWT_SECRET_KEY", "DefaultSecretKey")}')
        verify_jwt_in_request()
        current_user_id = get_jwt_identity()
        print(f"Current User ID: {current_user_id}")
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'error': '用户不存在', 'code': 401}), 401
        return f(*args, **kwargs)
    return decorated_function

def validate_form(form_class):
    """表单验证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            form = form_class()
            
            if request.is_json:
                form = form_class(data=request.get_json())
            elif request.form:
                form = form_class(formdata=request.form)
            elif request.args:
                form = form_class(formdata=request.args)
            
            if form.validate():
                return f(form, *args, **kwargs)
            
            return jsonify({
                'error': '表单验证失败',
                'code': 400,
                'details': form.errors
            }), 400
        return decorated_function
    return decorator