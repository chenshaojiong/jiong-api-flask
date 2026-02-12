from celery import shared_task
from celery.schedules import crontab
from app import db
from app.models.user import User
from app.models.post import Post
from datetime import datetime, timedelta
import os

@shared_task
def cleanup_expired_tokens():
    """清理过期的JWT令牌"""
    print(f"[{datetime.now()}] 执行清理过期令牌任务")
    return "清理完成"

@shared_task
def generate_daily_report():
    """生成每日报告"""
    print(f"[{datetime.now()}] 生成每日报告")
    
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    new_users = User.query.filter(User.created_at >= today_start).count()
    new_posts = Post.query.filter(Post.created_at >= today_start).count()
    total_users = User.query.count()
    total_posts = Post.query.count()
    
    report = {
        'date': today_start.date().isoformat(),
        'new_users': new_users,
        'new_posts': new_posts,
        'total_users': total_users,
        'total_posts': total_posts
    }
    
    print(f"每日报告: {report}")
    
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    
    # 发送邮件任务
    from app.tasks.email_tasks import send_email_task
    send_email_task.delay(
        admin_email,
        f"每日报告 - {today_start.date()}",
        f"<h2>每日报告</h2><p>日期: {today_start.date()}</p><p>今日新增用户: {new_users}</p><p>今日新增文章: {new_posts}</p><p>总用户数: {total_users}</p><p>总文章数: {total_posts}</p>"
    )
    
    return report

@shared_task
def cleanup_unverified_users():
    """清理未验证的用户"""
    print(f"[{datetime.now()}] 清理未验证用户任务执行")
    return 0

def setup_periodic_tasks(celery_app):
    """设置定时任务"""
    celery_app.conf.beat_schedule = {
        'cleanup-expired-tokens': {
            'task': 'app.tasks.scheduled_tasks.cleanup_expired_tokens',
            'schedule': crontab(hour=1, minute=0),
            'args': ()
        },
        'generate-daily-report': {
            'task': 'app.tasks.scheduled_tasks.generate_daily_report',
            'schedule': crontab(hour=23, minute=59),
            'args': ()
        },
        'cleanup-unverified-users': {
            'task': 'app.tasks.scheduled_tasks.cleanup_unverified_users',
            'schedule': crontab(hour=2, minute=0, day_of_week='sunday'),
            'args': ()
        },
    }