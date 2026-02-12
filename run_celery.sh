#!/bin/bash

# 启动Celery Worker
celery -A celery_worker.celery worker --loglevel=info -P eventlet

# 启动Celery Beat（定时任务）
# celery -A celery_worker.celery beat --loglevel=info

# 启动Celery Flower（监控界面）
# celery -A celery_worker.celery flower --port=5555