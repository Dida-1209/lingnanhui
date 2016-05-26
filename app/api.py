# coding:UTF-8


"""
名片社区API接口文件
@author: yubang
2016.02.29
"""

from flask import Blueprint, g, request, make_response, url_for, render_template, session, redirect, abort
from functools import wraps
from model.business_card import BusinessCardModel
from model.friend_model import FriendModel
from model.chat_model import ChatModel
from lib.upload_lib import upload_file
import json
import urllib
import requests


api_app = Blueprint('api', __name__)


def login_handle(fn):
    """
    处理用户登录修饰器
    :param fn:
    :return:
    """
    @wraps(fn)
    def handle(*args, **kwargs):
        session['open_id'] = 'abc'
        if 'open_id' not in session:
            session['now_url'] = request.path
            return redirect(url_for('api.login', _external=True))
        g.open_id = session['open_id']
        return fn(*args, **kwargs)

    return handle


def __handle_chat_message(obj):
    """
    处理聊天记录
    :param obj: 聊天记录
    :return:
    """
    obj['create_time'] = obj['create_time'].strftime("%Y-%m-%d %H:%M:%S")
    obj['uptime_time'] = obj['uptime_time'].strftime("%Y-%m-%d %H:%M:%S")
    return obj


@api_app.route('generatedNameCard', methods=['POST'])
@login_handle
def generated_name_card():
    """
    生成名片接口
    @author: yubang
    :return: str
    """
    open_id = g.open_id
    name = request.form.get('name', None)
    company = request.form.get('company', None)
    industry = request.form.get('industry', None)
    resources = request.form.get('resources', None)
    resources_label = request.form.get('resources_label', None)
    resources_key = request.form.get('resources_key', None)
    avatar = request.form.get('avatar', None)
    r = BusinessCardModel.make_a_card(open_id, name, company, industry, resources, resources_label, resources_key, avatar)

    result = dict()

    if r:
        result['code'] = 0
        result['msg'] = 'ok'
    else:
        result['code'] = -1
        result['msg'] = u'请勿重复生成名片！'

    response = make_response(json.dumps(result))
    response.headers['Content-Type'] = 'application/json'
    return response


@api_app.route('getNameCard')
@login_handle
def get_name_card():
    """
    拉取个人名片信息
    @author: yubang
    :return:
    """
    open_id = g.open_id
    obj = BusinessCardModel.get_name_card(open_id)

    result = {"code": 0, "msg": 'ok'}

    if not obj:
        result['code'] = -1
        result['msg'] = u'还没生成名片'
    else:
        obj['create_time'] = obj['create_time'].strftime("%Y-%m-%d %H:%M:%S")
        obj['update_time'] = obj['update_time'].strftime("%Y-%m-%d %H:%M:%S")
        result['content'] = obj

    response = make_response(json.dumps(result))
    response.headers['Content-Type'] = 'application/json'

    return response


@api_app.route('updateNameCard', methods=['POST'])
@login_handle
def update_name_card():
    """
    更新个人名片信息
    :return:
    """
    open_id = g.open_id
    name = request.form.get('name', None)
    company = request.form.get('company', None)
    industry = request.form.get('industry', None)
    resources = request.form.get('resources', None)
    resources_label = request.form.get('resources_label', None)
    resources_key = request.form.get('resources_key', None)
    avatar = request.form.get('avatar', None)

    result = {"code": 0, "msg": 'ok'}

    r = BusinessCardModel.update_a_card(open_id, name, company, industry, resources, resources_label, resources_key, avatar)

    if not r:
        result['code'] = -1
        result['msg'] = u'修改失败！'

    response = make_response(json.dumps(result))
    response.headers['Content-Type'] = 'application/json'
    return response


@api_app.route('getCode/<open_id>')
def get_code(open_id):
    """
    获取添加好友二维码接口
    @author: yubang
    :return: str
    """
    url = url_for("api.add_friend", _external=True)
    url = urllib.quote(url)
    return render_template('v1/code.html', url=url)


@api_app.route('add_friend/<friend_open_id>')
@login_handle
def add_friend(friend_open_id):
    """
    添加好友接口
    :param friend_open_id: 好友open_id
    :return:
    """
    if g.open_id == friend_open_id:
        # 自己扫描自己的二维码
        pass
    else:
        # 扫描别人的二维码
        FriendModel.add_friend(g.open_id, friend_open_id)
    return "ok"


@api_app.route('getContacts')
@login_handle
def get_contacts():
    """
    获取联系人接口
    @author: yubang
    :return: str
    """
    open_id = g.open_id

    objs = FriendModel.get_all_friends(open_id)
    result = {"code": 0, "msg": 'ok', "content": objs}
    response = make_response(json.dumps(result))
    response.headers['Content-Type'] = 'application/json'
    return response


@api_app.route('getChat/<friend_open_id>/<int:chat_page>/<int:chat_count_of_page>')
@login_handle
def get_chat(friend_open_id, chat_page, chat_count_of_page):
    """
    获取聊天记录接口
    @author: yubang
    :param friend_open_id: 朋友的微信open_id
    :param chat_page: 第几页聊天记录
    :param chat_count_of_page: 每页显示多少条聊天记录
    注意：当chat_page和chat_count_of_page都为0的时候返回所有数据
    :return:
    """
    open_id = g.open_id
    messages = ChatModel.get_a_page_of_chats(open_id, friend_open_id, chat_page, chat_count_of_page)

    messages = map(__handle_chat_message, messages)

    response = make_response(json.dumps(messages))
    response.headers['Content-Type'] = 'application/json'
    return response


@api_app.route('getNewChat/<friend_open_id>')
@login_handle
def get_new_chat(friend_open_id):
    """
    获取未读信息接口
    @author: yubang
    :param friend_open_id: 朋友的微信open_id
    :return:
    """
    open_id = g.open_id
    messages = ChatModel.get_all_new_message(open_id, friend_open_id)
    messages = map(__handle_chat_message, messages)
    response = make_response(json.dumps(messages))
    response.headers['Content-Type'] = 'application/json'
    return response


@api_app.route('getMessageNumber/<friend_open_id>')
@login_handle
def get_message_number(friend_open_id):
    """
    获取与某位好友的聊天记录数
    :param friend_open_id: 好友openid
    :return:
    """
    open_id = g.open_id
    new_number, all_number = ChatModel.get_message_number(open_id, friend_open_id)
    r = {"new_number": new_number, "all_number": all_number}

    response = make_response(json.dumps(r))
    response.headers['Content-Type'] = 'application/json'
    return response


@api_app.route('sendMessage/<friend_open_id>', methods=['POST'])
@login_handle
def send_message(friend_open_id):
    """
    发送信息给好友接口
    @author: yubang
    :param friend_open_id: 好友openid
    :return:
    """
    open_id = g.open_id
    message = request.form.get('message', None)
    r = ChatModel.send_message(open_id, friend_open_id, message, 0)
    result = {"code": 0, "msg": 'ok'}
    if not r:
        result['code'] = -1
        result['msg'] = u'发送失败！'
    response = make_response(json.dumps(result))
    response.headers['Content-Type'] = 'application/json'
    return response


@api_app.route('searchNameCard/<int:page>/<int:count_of_page>', methods=['POST'])
@login_handle
def search_name_card(page, count_of_page):
    """
    搜索名片接口
    :param page: 页数
    :param count_of_page: 每页记录数
    @author: yubang
    :return:
    """
    name = request.form.get('name', None)
    company = request.form.get('company', None)
    resources_label = request.form.get('resources_label', None)
    resources_key = request.form.get('resources_key', None)

    objs, nums, max_page = BusinessCardModel.search_cards(g.open_id, name, company, resources_label, resources_key, page, count_of_page)
    response = make_response(json.dumps({"objs": objs, "nums": nums, "max_page": max_page}))
    response.headers['Content-Type'] = 'application/json'
    return response


@api_app.route('getEditorRecommend/<int:page>/<int:count_of_page>')
@login_handle
def get_editor_recommend(page, count_of_page):
    """
    获取小编推荐接口
    :param page: 页数
    :param count_of_page: 每页记录数
    @author: yubang
    :return:
    """
    objs, nums, max_page = BusinessCardModel.get_recommend_cards(g.open_id, page, count_of_page)
    response = make_response(json.dumps({"objs": objs, "nums": nums, "max_page": max_page}))
    response.headers['Content-Type'] = 'application/json'
    return response


@api_app.route('getRecommendedForYou/<int:page>/<int:count_of_page>')
@login_handle
def get_recommended_for_you(page, count_of_page):
    """
    获取为你推荐接口
    @author: yubang
    :return:
    """
    objs, nums, max_page = BusinessCardModel.get_own_recommend_cards(g.open_id, page, count_of_page)
    response = make_response(json.dumps({"objs": objs, "nums": nums, "max_page": max_page}))
    response.headers['Content-Type'] = 'application/json'
    return response


@api_app.route('login')
def login():
    """
    登录接口，如果没有登录请引导用户到该接口
    :return:
    """
    # 记录下是哪一个地址
    if 'now_url' not in session:
        url = request.headers.get('Referer', '/')
        session['now_url'] = url

    # 引导用户到我们的登录系统
    referer = url_for('api.handle_oauth', _external=True)
    referer = urllib.quote(referer)

    login_url = "http://oauth.lingnanchuangye.com/oauth/login?referer=" + referer

    return redirect(login_url)


@api_app.route('handle_oauth')
def handle_oauth():
    """
    处理登录回调
    :return:
    """

    code = request.args.get('code', None)

    if not code:
        return abort(500)

    # 拉取用户信息
    api_url = "http://oauth.lingnanchuangye.com/api/api_get_user_message/" + code + "/abc123qwe"
    r = requests.get(api_url)

    data = r.content
    obj = json.loads(data)

    if 'openid' not in obj:
        return abort(500)

    # 记录信息到session
    session['user_data'] = obj

    # 记录用户openid到session
    session['open_id'] = obj['openid']

    return redirect(session['now_url'])


@api_app.route('update_pic', methods=['POST'])
def update_pic():
    """
    上传图片
    :return:
    """
    file = request.files['file']
    data = file.read()
    url = upload_file(data)
    return url
