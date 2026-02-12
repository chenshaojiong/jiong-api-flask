from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta

def generate_tokens(user_id, username):
    """生成访问令牌和刷新令牌"""
    access_token = create_access_token(
        identity=user_id,
        additional_claims={'username': username},
        expires_delta=timedelta(hours=1)
    )
    
    refresh_token = create_refresh_token(
        identity=user_id,
        expires_delta=timedelta(days=30)
    )
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': 43200
    }