# 创建虚拟环境

bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
bash
pip install -r requirements.txt
# 初始化数据库
bash
flask db init
flask db migrate -m "init database"
flask db upgrade
# 启动服务
bash
python run.py
# API测试示例
# 注册：

bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"123456","confirm_password":"123456"}'
# 登录：

bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"123456"}'
# 创建文章：

bash
curl -X POST http://localhost:5000/api/posts \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"测试文章","content":"这是文章内容"}'

# 安装和启动Celery
Windows:

bash
# 启动Celery Worker
celery -A celery_worker.celery worker --loglevel=info -P eventlet

# 启动Celery Beat（定时任务）- 注意这里是celery beat，不是celery-beat
celery -A celery_worker.celery beat --loglevel=info

# 启动Flower监控（可选）
pip install flower
celery -A celery_worker.celery flower --port=5555

Mac/Linux:

bash
# 启动Celery Worker
celery -A celery_worker.celery worker --loglevel=info

# 启动Celery Beat（定时任务）
celery -A celery_worker.celery beat --loglevel=info

# 启动Flower监控（可选）
celery -A celery_worker.celery flower --port=5555
使用Docker Compose（推荐）
bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
测试新功能
测试缓存：

bash
# 第一次请求，会从数据库读取
curl http://localhost:5000/api/posts

# 第二次请求，会从缓存读取
curl http://localhost:5000/api/posts
测试异步任务：

bash
# 注册时会自动触发发送欢迎邮件的异步任务
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser2","email":"test2@example.com","password":"123456","confirm_password":"123456"}'

# 创建文章时会自动触发发送通知邮件的异步任务
curl -X POST http://localhost:5000/api/posts \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"测试异步任务","content":"这篇文章会触发邮件通知"}'
查看任务状态：

bash
# 获取任务状态（需要先注册tasks蓝图）
curl http://localhost:5000/api/tasks/任务ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"