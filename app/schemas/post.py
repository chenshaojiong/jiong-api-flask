from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Optional

class PostForm(FlaskForm):
    title = StringField('标题', validators=[
        DataRequired(message='标题不能为空'),
        Length(min=2, max=200, message='标题长度必须在2-200个字符之间')
    ])
    content = TextAreaField('内容', validators=[
        DataRequired(message='内容不能为空'),
        Length(min=5, message='内容至少需要5个字符')
    ])

class PostUpdateForm(FlaskForm):
    title = StringField('标题', validators=[
        Optional(),
        Length(min=2, max=200, message='标题长度必须在2-200个字符之间')
    ])
    content = TextAreaField('内容', validators=[
        Optional(),
        Length(min=5, message='内容至少需要5个字符')
    ])

class PaginationForm(FlaskForm):
    page = IntegerField('页码', validators=[Optional()], default=1)
    per_page = IntegerField('每页数量', validators=[Optional()], default=10)