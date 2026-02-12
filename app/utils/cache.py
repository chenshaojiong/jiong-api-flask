from functools import wraps
from flask import request, jsonify
from app import cache
import hashlib
import json

def cache_key(*args, **kwargs):
    """生成缓存键"""
    key_parts = []
    
    # 添加请求路径
    key_parts.append(request.path)
    
    # 添加查询参数
    if request.args:
        key_parts.append(json.dumps(sorted(request.args.items())))
    
    # 添加请求体（如果是GET请求）
    if request.method == 'GET' and request.get_json(silent=True):
        key_parts.append(json.dumps(request.get_json(), sort_keys=True))
    
    # 添加用户ID（如果已认证）
    from flask_jwt_extended import get_jwt_identity
    try:
        user_id = get_jwt_identity()
        if user_id:
            key_parts.append(f"user:{user_id}")
    except:
        pass
    
    key = ':'.join(str(p) for p in key_parts)
    return hashlib.md5(key.encode()).hexdigest()

def cache_response(timeout=300, key_prefix=None):
    """缓存API响应"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 非GET请求不缓存
            if request.method != 'GET':
                return f(*args, **kwargs)
            
            # 生成缓存键
            cache_key_str = key_prefix if key_prefix else cache_key()
            
            # 尝试从缓存获取
            cached_response = cache.get(cache_key_str)
            if cached_response:
                return cached_response
            
            # 执行原函数
            response = f(*args, **kwargs)
            
            # 缓存响应
            cache.set(cache_key_str, response, timeout=timeout)
            
            return response
        return decorated_function
    return decorator

def clear_cache_by_prefix(prefix):
    """清除指定前缀的缓存"""
    try:
        if hasattr(cache.cache, '_read_clients'):
            # Redis缓存
            redis_client = cache.cache._read_clients[0]
            keys = redis_client.keys(f"*{prefix}*")
            if keys:
                redis_client.delete(*keys)
        else:
            # 其他缓存
            cache.clear()
    except Exception as e:
        print(f"清除缓存失败: {e}")

class ModelCache:
    """模型缓存工具类"""
    
    @staticmethod
    def get_model_key(model_name, model_id):
        return f"model:{model_name}:{model_id}"
    
    @staticmethod
    def get_model_list_key(model_name, **filters):
        filter_str = json.dumps(filters, sort_keys=True)
        return f"model:{model_name}:list:{hashlib.md5(filter_str.encode()).hexdigest()}"
    
    @staticmethod
    def cache_model(model_name, model_id, data, timeout=3600):
        key = ModelCache.get_model_key(model_name, model_id)
        cache.set(key, data, timeout=timeout)
    
    @staticmethod
    def get_cached_model(model_name, model_id):
        key = ModelCache.get_model_key(model_name, model_id)
        return cache.get(key)
    
    @staticmethod
    def clear_model_cache(model_name, model_id=None):
        if model_id:
            key = ModelCache.get_model_key(model_name, model_id)
            cache.delete(key)
        clear_cache_by_prefix(f"model:{model_name}")