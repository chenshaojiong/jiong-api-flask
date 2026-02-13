from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from app import db
from app.models.post import Post
from app.models.user import User
from app.schemas.post import PostForm, PostUpdateForm, PaginationForm
from app.utils.decorators import validate_form, login_required
from app.utils.cache import cache_response, ModelCache, clear_cache_by_prefix
from app.tasks.email_tasks import send_post_notification
from app.utils.response import success_response, fail_response, error_response, page_response

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/add', methods=['POST'])
@login_required
@validate_form(PostForm)
def create_post(form):
    """创建文章"""
    current_user_id = get_jwt_identity()
    current_user_id = int(current_user_id)  # 将字符串转换回整数
    user = User.query.get(current_user_id)
    
    post = Post(
        title=form.title.data,
        content=form.content.data,
        user_id=current_user_id
    )
    
    db.session.add(post)
    db.session.commit()
    
    # 清除列表缓存
    clear_cache_by_prefix('posts_list')
    ModelCache.clear_model_cache('post')
    
    # 异步发送通知邮件
    if user and user.email:
        send_post_notification.delay(
            user.id,
            user.email,
            user.username,
            post.title,
            post.id
        )
    
    return success_response(post.to_dict())

@posts_bp.route('', methods=['GET'])
@cache_response(timeout=60, key_prefix='posts_list')
@validate_form(PaginationForm)
def get_posts(form):
    """获取文章列表（支持分页，缓存60秒）"""
    page = form.page.data
    per_page = form.per_page.data
    
    # 尝试从缓存获取单个文章数据
    # 这里只是缓存整个响应，如果需要更细粒度的缓存，可以缓存每个文章对象
    pagination = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    posts = pagination.items
    total = pagination.total
    
    # 缓存单个文章
    for post in posts:
        ModelCache.cache_model('post', post.id, post.to_dict(), timeout=3600)


    items = [post.to_dict() for post in posts]
    
    return page_response(page, per_page, total, pagination.pages, items)

@posts_bp.route('/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """获取单篇文章（使用模型缓存）"""
    # 尝试从缓存获取
    cached_post = ModelCache.get_cached_model('post', post_id)
    if cached_post:
        return jsonify({
            'code': 200,
            'data': cached_post,
            'cached': True
        }), 200
    
    post = Post.query.get(post_id)
    
    if not post:
        return jsonify({'error': '文章不存在', 'code': 404}), 404
    
    post_dict = post.to_dict()
    
    # 缓存文章
    ModelCache.cache_model('post', post_id, post_dict, timeout=3600)
    
    return jsonify({
        'code': 0,
        'data': post_dict,
        'cached': False
    }), 200

@posts_bp.route('/<int:post_id>', methods=['PUT'])
@login_required
@validate_form(PostUpdateForm)
def update_post(form, post_id):
    """更新文章"""
    current_user_id = get_jwt_identity()
    current_user_id = int(current_user_id)  # 将字符串转换回整数
    post = Post.query.get(post_id)
    
    if not post:
        return jsonify({'error': '文章不存在', 'code': 404}), 404
    
    # 检查权限
    if post.user_id != current_user_id:
        return jsonify({'error': '没有权限修改此文章', 'code': 403}), 403
    
    # 更新字段
    if form.title.data:
        post.title = form.title.data
    if form.content.data:
        post.content = form.content.data
    
    db.session.commit()
    
    # 清除缓存
    ModelCache.clear_model_cache('post', post_id)
    clear_cache_by_prefix('posts_list')
    
    return success_response(post.to_dict())

@posts_bp.route('/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    """删除文章"""
    current_user_id = get_jwt_identity()
    current_user_id = int(current_user_id)  # 将字符串转换回整数
    post = Post.query.get(post_id)
    
    if not post:
        return error_response(404, '文章不存在')
    
    # 检查权限
    if post.user_id != current_user_id:
        return error_response(403, '没有权限删除此文章')
    
    db.session.delete(post)
    db.session.commit()
    
    # 清除缓存
    ModelCache.clear_model_cache('post', post_id)
    clear_cache_by_prefix('posts_list')
    
    return success_response()