# -*- coding:UTF-8 -*-
# 视图
import json
import os
import uuid

__author__ = "ChenQing"
__date__ = "2018-07-19 20:45"

from application import app, db
from flask import render_template, request, flash, get_flashed_messages, redirect, send_from_directory
from application.models import Image, User, Comment
from flask_login import login_user, login_required, current_user, logout_user
import hashlib
import random


@app.route('/')
def index():  # 主页
    images = Image.query.order_by(Image.id.desc()).limit(10).all()
    return render_template('index.html', images=images)


@app.route('/image/<int:image_id>')
def detail(image_id):  # 图片详情页面
    image = Image.query.get(image_id)
    image.comments = Comment.query.filter_by(image_id=image_id, status=0).order_by(Comment.id.desc()).limit(10).all()
    return render_template('pageDetail.html', image=image)


@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):  # 个人主页
    user = User.query.get(user_id)
    if user is None:
        return redirect('/')
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=1, per_page=3)
    return render_template('profile.html', user=user, has_next=paginate.has_next, images=paginate.items)


@app.route('/loginreg/')
def login_reg(msg=''):  # 登陆注册页面
    if current_user.is_authenticated:
        return redirect('/')
    res = msg
    for msg in get_flashed_messages(with_categories=False, category_filter=['loginreg']):
        res += msg
    print(request.values.get('next'))
    return render_template('login.html', msg=msg, next=request.values.get('next'))


@app.route('/logout/')
def logout():  # 登出
    logout_user()
    return redirect('/')


@app.route('/login/', methods={'get', 'post'})
def login():  # 登陆
    # 先获取用户名和密码
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    if username == '' or password == '':
        return redirect_to_page_with_msg('/loginreg', u'用户名或密码不能为空', 'loginreg')
    user = User.query.filter_by(username=username).first()
    if user is None:
        return redirect_to_page_with_msg('/loginreg', u'用户不存在', 'loginreg')

    # md5加盐校验
    m = hashlib.md5()
    m.update((password + user.salt).encode("utf8"))
    if str(m.hexdigest()) != user.password:
        return redirect_to_page_with_msg('/loginreg', u'用户名或密码错误', 'loginreg')

    login_user(user)

    # 判断next
    next_page = request.values.get('next')
    print(next_page)
    print(next_page.startswith('/'))
    if next_page is not None and (next_page.startswith('/') > 0 or next_page.startswith('http://') > 0 ):
        return redirect(next_page)
    return redirect('/')


@app.route('/reg/', methods={'POST', 'GET'})
def reg():  # 注册
    # 先获取用户名和密码
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()

    # 校验非空
    if username == '' or password == '':
        return redirect_to_page_with_msg('/loginreg/', u'用户名或密码不能为空', 'loginreg')
    # 检验用户名和密码长度
    if len(username) < 6:
        return redirect_to_page_with_msg('/loginreg', u'用户名长度必须大于6', 'loginreg')
    if len(password) < 10:
        return redirect_to_page_with_msg('/loginreg', u'密码长度必须大于10', 'loginreg')
    # 密码强度检测
    if password_level(password) < 3:
        return redirect_to_page_with_msg('/loginreg/', u'密码强度太低，至少包含数字，字母，符号三种', 'loginreg')

    # 校验用户是否存在
    user = User.query.filter_by(username=username).first()
    if user is not None:
        print(user.username + ',' + user.password)
        return redirect_to_page_with_msg('/loginreg/', u'该用户已存在', 'loginreg')

    # 加盐md5加密
    salt = '.'.join(random.sample('0123456789asdfghjklqwertyuiopzxcvbnm', 10))
    print("salt" + salt)
    m = hashlib.md5()
    m.update((password + salt).encode("utf8"))
    password = m.hexdigest()
    user = User(username, password, salt)
    # 添加用户到数据库
    db.session.add(user)
    db.session.commit()

    # 在session中注册用户
    login_user(user)

    # 判断有没有next
    next_page = request.values.get('next')
    if next_page is not None and (next_page.startswith('/') > 0 or next_page.startswith('http://') > 0 ):
        return redirect(next_page)
    return redirect('/')


@app.route('/profile/images/<int:user_id>/<int:page>/<int:page_size>/')
@login_required
def user_image(user_id, page, page_size):  # 分页获取图片
    # 参数检查
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=page, per_page=page_size)

    res_map = {'has_next': paginate.has_next}
    images = []
    for image in paginate.items:
        imgvo = {'id': image.id, 'url': image.url, 'comment_count': len(image.comments)}
        images.append(imgvo)
    res_map['images'] = images
    return json.dumps(res_map)


def save_to_local(file, file_name):  # 保存图片到本地
    save_dir = app.config['UPLOAD_DIR']
    file.save(os.path.join(save_dir, file_name))
    return '/image/' + file_name


@app.route('/image/<image_name>')  # 显示图片
def view_image(image_name):
    return send_from_directory(app.config['UPLOAD_DIR'], image_name)


@app.route('/upload/', methods={'post'})
@login_required
def upload():  # 图片上传
    file = request.files['file']
    file_ext = ''
    if file.filename.find('.') > 0:
        file_ext = file.filename.rsplit('.', 1)[1].strip().lower()
    if file_ext in app.config['ALLOW_EXT']:
        file_name = str(uuid.uuid1()).replace('-', '') + '.' + file_ext
        url = save_to_local(file, file_name)
        if url is not None:
            db.session.add(Image(url, current_user.id))
            db.session.commit()

    return redirect('/profile/%d' % current_user.id)


@app.route('/addcomment/', methods={'post'})
def add_comment():
    if not current_user.is_authenticated:
        return json.dumps({'code':1, 'msg':'请先登录再评论！'})
    image_id = request.values.get('image_id').strip()
    content = request.values.get('content').strip()
    res_map = {}
    if image_id == '' or content == '':
        res_map['code'] = 1
        res_map['msg'] = '访问有误！'
        return json.dumps(res_map)
    if Image.query.filter_by(id=image_id).first() is None:
        res_map['code'] = 2
        res_map['msg'] = '图片不存在！'
        return json.dumps(res_map)


    # 添加到数据库
    comment = Comment(content, image_id, current_user.id)
    db.session.add(comment)
    db.session.commit()
    # 获取主键id
    comment_id = comment.id

    print(comment)
    res_map = {'code': 0, 'username': current_user.username, 'user_id': current_user.id, 'comment_id':comment_id}
    return json.dumps(res_map)


@app.route('/deletecomment/', methods={'post','get'})
def delete_comment():
    if not current_user.is_authenticated:
        return json.dumps({'code':1, 'msg':'请先登录操作！'})
    comment_id = request.values.get('comment_id')
    if comment_id == '':
        return json.dumps({'code': 1, 'msg':u'访问错误'})
    comment = Comment.query.filter_by(id=comment_id).first()
    if comment is None:
        return json.dumps({'code': 2, 'msg': u'评论不存在'})
    elif comment.user_id != current_user.id:
        return json.dumps({'code':3, 'msg':u'您没有权限删除'})
    else:
        comment.status = 1
        db.session.commit()
        return json.dumps({'code':0})


def redirect_to_page_with_msg(target, msg, category):  # 携带消息重定向到指定url
    # 携带消息重定向
    if msg is not None:
        flash(msg, category=category)
    return redirect(target)


def password_level(password):  # 密码强度
    has_digit = False
    has_symbol = False
    has_letter = False
    for ch in password:
        if not has_digit and ord('0') <= ord(ch) <= ord('9'):
            has_digit = True
        if not has_letter \
                and ((ord('a') <= ord(ch) <= ord('z'))
                     or (ord('A') <= ord(ch) <= ord('Z'))):
            has_letter = True
        if not has_symbol and ((32 <= ord(ch) <= 47) or (58 <= ord(ch) <= 96)
                               or (123 <= ord(ch) <= 126)):
            has_symbol = True
    level = 0
    if has_digit:
        level += 1
    if has_symbol:
        level += 1
    if has_letter:
        level += 1
    return level
