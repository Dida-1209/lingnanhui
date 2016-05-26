# coding:UTF-8


"""
后台管理模块
@author: yubang
2016.03.14
"""


from flask import Blueprint, render_template, request, redirect, session, make_response, url_for, send_file, abort
from config import other_config
from functools import wraps
from model.business_card import BusinessCardModel
from model.wechat_reply_model import WechatReplyModel
from model.group_links_model import GroupLinksModel
from model.resource_helper_message_model import ResourceHelperMessageModel
from lib.output import make_a_data
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
            return redirect(url_for('admin_app.index'))
        return fn(*k, **v)
    return handle


def check_client_power(fn):
    """
    判断客户端有没有权限访问接口
    :param fn:
    :return:
    """
    @wraps(fn)
    def handle(*k, **v):

        if request.method == 'GET':
            return abort(404)

        if request.form.get('token', None) != other_config.client_token:
            return abort(404)

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
    return send_file("templates/admin/v1/cards.html", cache_timeout=0)


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


@admin_app.route('robot_set')
@__handle_login
def robot_set():
    """
    机器人自动回复配置
    :return:
    """
    return send_file('templates/admin/v1/robot_set.html')


@admin_app.route('add_reply', methods=['POST'])
@__handle_login
def add_reply():
    """
    添加自动回复
    :return:
    """

    wechat_group_name = request.form.get('wechat_group_name', None)
    reply_content = request.form.get('reply_content', None)
    status = request.form.get('status', None)
    reply_key = request.form.get('reply_key', None)
    WechatReplyModel.add_setting(wechat_group_name, reply_content, status, reply_key)

    return "ok"


@admin_app.route('get_all_replys')
@__handle_login
def get_all_replys():
    """
    获取所有的回复配置
    :return:
    """

    datas = WechatReplyModel.get_replys()
    datas = map(WechatReplyModel.handle_data_use_in_json, datas)

    response = make_response(json.dumps(datas))
    response.headers['Content-Type'] = 'application/json'
    return response


@admin_app.route('delete_reply')
@__handle_login
def delete_reply():
    reply_id = request.args.get('id', None)
    WechatReplyModel.remove_setting(reply_id)
    return "ok"


@admin_app.route('update_reply', methods=['POST'])
@__handle_login
def update_reply():
    """
    修改自动回复配置
    :return:
    """

    reply_id = request.form.get('id', None)
    wechat_group_name = request.form.get('wechat_group_name', None)
    reply_content = request.form.get('reply_content', None)
    status = request.form.get('status', None)
    reply_key = request.form.get('reply_key', None)

    WechatReplyModel.update_setting(wechat_group_name, reply_content, status, reply_id, reply_key)

    return "ok"


@admin_app.route('get_reply_config_to_client', methods=['GET', 'POST'])
@check_client_power
def get_reply_config_to_client():
    """
    提供给客户端获取自动回复配置接口
    :return:
    """

    datas = WechatReplyModel.get_replys()
    datas = map(WechatReplyModel.handle_data_use_in_json, datas)

    response = make_response(json.dumps(datas))
    response.headers['Content-Type'] = 'application/json'
    return response


@admin_app.route('group_link_setting')
@__handle_login
def group_link_setting():
    """
    群链接配置页面
    :return:
    """
    return send_file('templates/admin/v1/group_link_setting.html', cache_timeout=0)


@admin_app.route('add_link', methods=['POST'])
@__handle_login
def add_link():
    """
    添加链接
    :return:
    """

    group_title = request.form.get('group_title', None)
    group_status = request.form.get('group_status', None)

    GroupLinksModel.add_link(group_title, group_status)

    return "ok"


@admin_app.route('get_links', methods=['POST'])
@__handle_login
def get_links():
    """
    获取一页链接
    :return:
    """

    page = request.form.get('page', None)
    count = request.form.get('count', None)

    r = GroupLinksModel.get_a_page_of_link(int(page), int(count))

    r['url'] = url_for('web_app.to_wechat_link', group_token='', _external=True)

    response = make_response(json.dumps(r))
    response.headers['Content-Type'] = 'application/json'
    return response


@admin_app.route('delete_link/<token>')
@__handle_login
def delete_link(token):
    """
    删除群链接
    :param token: 群token
    :return:
    """
    GroupLinksModel.remove_link(token)
    return "ok"


@admin_app.route('edit_link', methods=['POST'])
@__handle_login
def edit_link():
    """
    编辑链接
    :return:
    """
    group_title = request.form.get('group_title', None)
    group_token = request.form.get('group_token', None)
    group_status = request.form.get('group_status', None)

    GroupLinksModel.update_link(group_title, group_status, group_token)

    return "ok"


@admin_app.route('resource_helper_message_ui')
@__handle_login
def resource_helper_message_ui():
    """
    资源小助手信息页面
    :return:
    """
    return send_file('templates/admin/v1/resource_helper_message_ui.html', cache_timeout=0)


@admin_app.route('resource_helper_message_send', methods=['POST'])
@__handle_login
def resource_helper_message_send():
    """
    资源小助手发送消息接口
    :return:
    """

    open_id = request.form.get('open_id', None)
    message_content = request.form.get('message_content', None)

    ResourceHelperMessageModel.add_message(0, '', open_id, message_content, 0)

    return make_a_data("ok")


@admin_app.route('get_resource_helper_message_of_page/<int:page>/<int:count_of_page>')
@__handle_login
def get_resource_helper_message_of_page(page, count_of_page):
    """
    获取一页资源小助手信息
    :return:
    """
    r = ResourceHelperMessageModel.get_resource_helper_message_of_page(page, count_of_page)
    return make_a_data(r)


@admin_app.route('remove_message')
@__handle_login
def remove_message():
    """
    删除信息
    :return:
    """
    message_id = request.args.get('message_id', None)
    r = ResourceHelperMessageModel.remove_message(int(message_id))
    return make_a_data(r)
