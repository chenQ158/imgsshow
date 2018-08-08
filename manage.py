# -*- coding:UTF-8 -*-
# 脚本数据
import unittest

__author__ = "ChenQing"
__date__ = "2018-07-19 20:44"

from application import app, db
from flask_script import Manager
from sqlalchemy import or_, and_
from application.models import User, Image, Comment
from random import *

manager = Manager(app)


def get_image_url():
    rand_num = randint(0, 1000)
    return "http://images.nowcoder.com/head/%dm.png" % rand_num


@manager.command
def run_test():
    tests = unittest.TestLoader().discover('./tests/')
    unittest.TextTestRunner().run(tests)

@manager.command
def init_database():
    db.drop_all()
    db.create_all()
    # 添加用户
    for i in range(0, 100):
        db.session.add(User('User' + str(i), 'a' + str(i),'.'.join(sample('0123456789asdfghjklqwertyuiopzxcvbnm', 10)), get_image_url()))
        for j in range(0, 5):
            db.session.add(Image(get_image_url(), i + 1))
            for k in range(0, 3):
                db.session.add(Comment('This is a comment' + str(k), 1 + 1 * i + j, i + 1))
    db.session.commit()

    # 修改两种方式
    for i in range(50, 100, 2):
        user = User.query.get(i)
        user.username = '[New]' + user.username
    db.session.commit()

    User.query.filter_by(id=51).update({'username': '[New2]'})
    db.session.commit()

    # 删除
    for i in range(50, 100, 2):
        comment = Comment.query.get(i + 1)
        db.session.delete(comment)
    db.session.commit()
    # 另一种直接使用delete()方法

    # 查询
    print(1)
    print(User.query.all())
    print(2)
    print(User.query.get(3))
    print(3)
    print(User.query.filter_by(id=5).first())
    print(4)
    print(User.query.order_by(User.id.desc()).offset(1).limit(2).all())
    print(5)
    print(User.query.filter(User.username.endswith('0')).limit(3).all())
    print(6)
    print(User.query.filter(or_(User.id == 88, User.id == 99)).all())
    print(7)
    print(User.query.filter(and_(User.id > 88, User.id < 99)).all())
    print(8)
    print(User.query.filter(and_(User.id > 88, User.id < 99)).first_or_404())
    print(9)
    print(User.query.order_by(User.id.desc()).paginate(page=1, per_page=10).items)

    user = User.query.get(1)  # 从1开始，第1个用户
    print(10)
    print(user.images.all())
    image = Image.query.get(1)
    print(11)
    print(image.user)


if __name__ == '__main__':
    manager.run()
