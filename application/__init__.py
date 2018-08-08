# -*- coding:UTF-8 -*-
# 模块导出文件
__author__ = "ChenQing"
__date__ = "2018-07-19 20:43"

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
# 加载文件配置
app.jinja_env.add_extension('jinja2.ext.loopcontrols')  # 扩展，在模板中使用break
app.config.from_pyfile('app.conf')
app.secret_key = 'sadfljsalfjlxzuvcoi'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = '/loginreg/'

db = SQLAlchemy(app)

from application import views, models
