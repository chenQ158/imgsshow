# -*- coding:UTF-8 -*-
# 数据模型
from flask_login import UserMixin

__author__ = "ChenQing"
__date__ = "2018-07-19 20:44"

from application import db, login_manager
from datetime import datetime
from random import *

def get_image_url():
    randnum = randint(0, 1000)
    return "http://images.nowcoder.com/head/%dm.png" % randnum
# 类与数据库中的表相关联


class User(db.Model, UserMixin):
    # __tablename__ = 'tb_user' # 自定义表名
    # id编号，主键，自增
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(32))
    head_url = db.Column(db.String(256))
    salt = db.Column(db.String(32))
    images = db.relationship("Image", backref='user', lazy='dynamic')


    # backref是当调用Image对象时获取User

    def __init__(self, username, password, salt, url=get_image_url()):
        self.head_url = url
        self.username = username
        self.password = password
        self.salt = salt

    def __repr__(self):
        return '<User %d %s>' % (self.id, self.username)


    # Flask Login接口
    # 前三个的@property装饰器可有可无 不知道有什么用
    # 也可以通过直接继承UserMixin的方式
    '''
    @property
    def is_authenticated(self):
        #  True如果用户已通过身份验证，则此属性应返回，即他们已提供有效凭据。
        # （只有经过身份验证的用户才能满足以下条件login_required。）
        print('is_authenticated')
        return True
    @property
    def is_active(self):
        # True如果这是一个活跃的用户，则该属性应该返回- 除了经过身份验证之外，
        # 他们还激活了他们的帐户，没有被暂停，或者您的应用程序拒绝帐户的任何条件。
        # 非活动帐户可能无法登录（当然不会被强制使用）。
        print('is_active')
        return True
    @property
    def is_anonymous(self):
        # True如果这是匿名用户，则应返回此属性。（实际用户应该返回False。）
        print('is_anonymous')
        return False

    def get_id(self):
        return self.id
    '''

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(512))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_date = db.Column(db.DateTime)
    comments = db.relationship('Comment')

    def __init__(self, url, user_id):
        self.url = url
        self.user_id = user_id
        self.created_date = datetime.now()

    def __repr__(self):
        return '<Image %d %s>' % (self.id, self.url)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(1024))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.Integer, default=0)  # 0:正常 1:被删除
    created = db.Column(db.DateTime)
    user = db.relationship('User')


    def __init__(self, content, image_id, user_id):
        self.content = content
        self.image_id = image_id
        self.user_id = user_id
        self.created = datetime.now()

    def __repr__(self):
        return '<Comment %d %s>' % (self.id, self.content)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)