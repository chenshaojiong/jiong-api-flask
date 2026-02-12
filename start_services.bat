@echo off
echo 启动Flask应用...
start python run.py

echo 启动Celery Worker...
start celery -A celery_worker.celery worker --loglevel=info -P eventlet

echo 启动Celery Beat...
start celery -A celery_worker.celery beat --loglevel=info

echo 启动Flower监控...
start celery -A celery_worker.celery flower --port=5555

echo 所有服务已启动！