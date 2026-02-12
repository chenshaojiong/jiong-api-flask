#!/usr/bin/env python
from app import create_app

app = create_app()
celery = app.celery

# 确保 Celery 使用 Flask 配置中的新格式设置
celery.conf.update(
    broker_url=app.config['broker_url'],
    result_backend=app.config['result_backend'],
    timezone=app.config['timezone'],
    enable_utc=app.config['enable_utc'],
    task_track_started=app.config['task_track_started'],
    task_time_limit=app.config['task_time_limit'],
    broker_connection_retry_on_startup=app.config['broker_connection_retry_on_startup'],
    beat_schedule=app.config.get('beat_schedule', {})
)

# 导入任务模块
from app.tasks import email_tasks
from app.tasks import scheduled_tasks

__all__ = ['celery', 'email_tasks', 'scheduled_tasks']

if __name__ == '__main__':
    celery.start()