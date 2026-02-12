#!/bin/bash
echo "启动Flask应用..."
python run.py &

echo "启动Celery Worker..."
celery -A celery_worker.celery worker --loglevel=info &

echo "启动Celery Beat..."
celery -A celery_worker.celery beat --loglevel=info &

echo "启动Flower监控..."
celery -A celery_worker.celery flower --port=5555 &

echo "所有服务已启动！"