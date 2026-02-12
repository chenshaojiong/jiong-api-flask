from celery import shared_task
from flask import current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import os

@shared_task
def send_email_task(recipient, subject, content):
    """发送邮件任务"""
    print(f"发送邮件到: {recipient}")
    print(f"主题: {subject}")
    print(f"内容: {content[:100]}...")
    
    # 实际邮件发送代码
    """
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    sender_email = os.getenv('SMTP_USER')
    sender_password = os.getenv('SMTP_PASSWORD')
    
    message = MIMEMultipart('alternative')
    message['Subject'] = Header(subject, 'utf-8')
    message['From'] = sender_email
    message['To'] = recipient
    
    part = MIMEText(content, 'html', 'utf-8')
    message.attach(part)
    
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient, message.as_string())
    """
    
    return {
        'status': 'success',
        'recipient': recipient,
        'subject': subject
    }

@shared_task
def send_welcome_email(user_id, email, username):
    """发送欢迎邮件"""
    subject = f"欢迎加入 {os.getenv('APP_NAME', 'Flask API')}"
    content = f"""
    <h1>欢迎您，{username}！</h1>
    <p>感谢您注册我们的服务。</p>
    <p>您的用户ID是: {user_id}</p>
    <p>祝您使用愉快！</p>
    """
    return send_email_task(email, subject, content)

@shared_task
def send_post_notification(user_id, email, username, post_title, post_id):
    """发送文章发布通知"""
    subject = f"文章已发布: {post_title}"
    content = f"""
    <h2>您的文章已成功发布</h2>
    <p>您好，{username}！</p>
    <p>您的文章《{post_title}》已成功发布。</p>
    <p>查看文章: <a href="{os.getenv('APP_URL', 'http://localhost:5000')}/api/posts/{post_id}">点击这里</a></p>
    """
    return send_email_task(email, subject, content)