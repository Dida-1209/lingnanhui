# coding:UTF-8


"""
后台管理模块
@author: yubang
2016.03.14
"""


from flask import Blueprint, render_template, request, redirect, session, make_response, url_for
from config import other_config
from model.business_card import BusinessCardModel
from functools import wraps
import time
import hashlib
import json


admin_app = Blueprint('admin_app', __name__)


def __handle_login(fn):
    """
    处理后台登录问题
    :param fn: 函数
    :return:
    """
    @wraps(fn)
    def handle(*k, **v):
        if 'admin' not in session:
            print 123
            return redirect(url_for('admin_app.index'))
        return fn(*k, **v)
    return handle


@admin_app.route('')
def index():
    """
    后台主页面
    :return:
    """
    return render_template("admin/v1/index.html")


@admin_app.route('login', methods=['POST'])
def login():
    """
    后台用户登录
    :return:
    """
    username = request.form.get('username', None)
    password = request.form.get('password', None)
    password = hashlib.md5(password).hexdigest()

    if username != other_config.username or password != other_config.password:
        # 用户名或密码错误
        return redirect('/admin/v1/')

    session['admin'] = time.time()

    return redirect('/admin/v1/cards')


@admin_app.route('cards')
@__handle_login
def cards():
    """
    名片后台管理小页面
    :return:
    """
    return render_template("/admin/v1/cards.html")


@admin_app.route('get_cards', methods=['POST'])
@__handle_login
def get_cards():
    """
    获取名片列表
    :return:
    """
    page = request.form.get('page', None)
    search_nickname = request.form.get('search_nickname', None)
    status = request.form.get('status', None)

    page = int(page)

    if int(status) == 0:
        order_by_str = " order by id asc "
    else:
        order_by_str = " order by id desc "

    objs, nums = BusinessCardModel.get_a_page_of_cards(page, 10, search_nickname, order_by_str)

    max_page = nums / 10
    if nums % 10:
        max_page += 1

    r = make_response(json.dumps({"objs": objs, "max_page": max_page, "page": page}))
    r.headers['Content-Type'] = 'application/json'
    return r


@admin_app.route('delete_card/<int:card_id>')
@__handle_login
def delete_card(card_id):
    """
    删除一张名片
    :param card_id: 名片id
    :return:
    """
    r = BusinessCardModel.delete_card(card_id)
    response = make_response(json.dumps({"code": r}))
    response.headers['Content-Type'] = 'application/json'
    return response


@admin_app.route('recommend_card/<int:card_id>/<int:status>')
@__handle_login
def recommend_card(card_id, status):
    """
    处理小编推荐接口
    :param card_id: 名片ID
    :param status:  名片推荐状态
    :return:
    """
    r = BusinessCardModel.recommend_card(card_id, status)
    response = make_response(json.dumps({"code": r}))
    response.headers['Content-Type'] = 'application/json'
    return response
