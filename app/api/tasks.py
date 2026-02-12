from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from celery.result import AsyncResult

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')

@tasks_bp.route('/<task_id>', methods=['GET'])
@jwt_required()
def get_task_status(task_id):
    """获取任务状态"""
    from app import create_app
    app = create_app()
    celery = app.celery
    
    task = AsyncResult(task_id, app=celery)
    
    response = {
        'task_id': task_id,
        'status': task.status,
        'result': task.result if task.ready() else None
    }
    
    return jsonify({
        'code': 200,
        'data': response
    }), 200