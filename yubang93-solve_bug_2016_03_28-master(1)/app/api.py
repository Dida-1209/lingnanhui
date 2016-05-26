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
from model.group_record import GroupRecordModel
from model.group_links_model import GroupLinksModel
from lib.upload_lib import upload_file
from config.other_config import DEBUG
from model.resource_helper_message_model import ResourceHelperMessageModel
from model.apply_friends import ApplyFriendsModel
from lib.output import make_a_data
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
        if DEBUG:
            session['open_id'] = 'abc'
            session['user_data'] = {"headimgurl": 'http://7xplbl.com1.z0.glb.clouddn.com/card/b078b8d61ce8110ee3547f3770d82030'}
            if 'open_id' not in session:
                session['open_id'] = 'fff'
                session['user_data'] = {"headimgurl": ''}
        if 'open_id' not in session:
            session['now_url'] = request.url
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
    resources_key = request.form.get('resources_key', None)
    avatar = request.form.get('avatar', None)
    role = request.form.get('role', None)
    invitation_code = request.form.get('invitation_code', None)

    # 省市
    province = request.form.get('province', None)
    city = request.form.get('city', None)
    area = request.form.get('area', None)

    # 检测邀请码
    if not BusinessCardModel.check_invitation_code(invitation_code):
        response = make_response(json.dumps({"code": -5, "msg": u'邀请码不正确！'}))
        response.headers['Content-Type'] = 'application/json'
        return response

    r = BusinessCardModel.make_a_card(open_id, name, company, industry, resources_key, avatar, role, invitation_code, province, city, area)

    result = dict()

    if r:
        result['code'] = 0
        result['msg'] = 'ok'
    else:
        result['code'] = 0
        result['msg'] = u'请勿重复生成名片！'

    # 处理加入群情况
    if 'group_token' in session:
        try:
            GroupRecordModel.join_group(g.open_id, session['group_token'])
        except:
            pass

    # 特殊处理扫描海报二维码后生成名片的情况
    from_open_id = request.form.get('from_open_id', None)
    if from_open_id and BusinessCardModel.has_card(from_open_id):
        ApplyFriendsModel.apply_friend(g.open_id, from_open_id, u'通过扫描您的海报申请资源对接')

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
    resources_key = request.form.get('resources_key', None)
    avatar = request.form.get('avatar', None)
    role = request.form.get('role', None)
    result = {"code": 0, "msg": 'ok'}

    invitation_code = request.form.get('invitation_code', None)

    # 省市
    province = request.form.get('province', None)
    city = request.form.get('city', None)
    area = request.form.get('area', None)

    # 检测邀请码
    if not BusinessCardModel.check_invitation_code(invitation_code):
        response = make_response(json.dumps({"code": -5, "msg": u'邀请码不正确！'}))
        response.headers['Content-Type'] = 'application/json'
        return response

    r = BusinessCardModel.update_a_card(open_id, name, company, industry, resources_key, avatar, role, invitation_code, province, city, area)

    if not r:
        # 防止什么都没修改
        result['code'] = 0
        result['msg'] = u'修改失败！'

    response = make_response(json.dumps(result))
    response.headers['Content-Type'] = 'application/json'
    return response


@api_app.route('getContacts', methods=['POST'])
@login_handle
def get_contacts():
    """
    获取联系人接口
    @author: yubang
    :return: str
    """
    open_id = g.open_id

    objs = FriendModel.get_all_friends(open_id)

    # 处理搜索条件
    search_key = request.form.get('search_key', None).encode("UTF-8")
    industry = request.form.get('industry', None).encode("UTF-8")
    role = request.form.get('role', None).encode("UTF-8")
    output_objs = []
    for obj in objs:

        if obj['name'].encode('UTF-8').find(search_key) == -1 and obj['company'].encode('UTF-8').find(search_key) == -1 and obj['redundancy_labels'].encode('UTF-8').find(search_key) == -1:
            continue

        if obj['industry'].encode('UTF-8').find(industry) == -1:
            continue

        if obj['role'].encode('UTF-8').find(role) == -1:
            continue

        output_objs.append(obj)
    objs = output_objs

    # 添加自己的信息
    card = BusinessCardModel.get_name_card(g.open_id)
    card['name_pinyin'] = ''
    card = BusinessCardModel.handle_data_use_in_json(card)
    objs.insert(0, card)

    result = {"code": 0, "msg": 'ok', "content": objs}
    response = make_response(json.dumps(result))
    response.headers['Content-Type'] = 'application/json'
    return response


@api_app.route('getChat/<friend_open_id>/<int:chat_page>/<int:chat_count_of_page>', methods=['POST'])
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
    last_message_id = request.form.get('last_message_id', None)
    messages = ChatModel.get_a_page_of_chats(open_id, friend_open_id, chat_page, chat_count_of_page, int(last_message_id))

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
    industry = request.form.get('industry', None)
    role = request.form.get('role', None)
    search_key = request.form.get('search_key', None)

    if search_key is None or industry is None or role is None:
        return abort(404)

    objs, nums, max_page = BusinessCardModel.search_cards(g.open_id, industry.encode("UTF-8"), role.encode("UTF-8"), search_key.encode("UTF-8"), page, count_of_page)
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


@api_app.route('get_own_card_in_make_card')
@login_handle
def get_own_card_in_make_card():
    """
    拉取制作名片的相关信息
    :return:
    """
    obj = BusinessCardModel.get_name_card(g.open_id)

    if not obj:
        obj = {
            "avatar": session['user_data']['headimgurl'],
            "name": '',
            "company": '',
            "industry": u'互联网/软件',
            "role": u'产品',
            "resources_key": '',
            "invitation_code": '',
            "province": '',
            "city": '',
            "area": '',
        }
        obj['target_url'] = '/api/v1/generatedNameCard'
    else:
        obj['target_url'] = '/api/v1/updateNameCard'

    # 处理登录跳转接口
    if 'group_token' in session:
        obj['after_login_url'] = url_for('web_app.all_cards', group_token=session['group_token'])
    else:
        obj['after_login_url'] = url_for('web_app.contact_list')

    obj = BusinessCardModel.handle_data_use_in_json(obj)
    response = make_response(json.dumps(obj))
    response.headers['Content-Type'] = 'application/json'
    return response


@api_app.route('get_all_card_in_a_group', methods=['POST'])
@login_handle
def get_all_card_in_a_group():
    """
    获取一个群所有名片
    :return:
    """
    group_token = request.form.get('group_token', None)

    # 关键字
    search_key = request.form.get('search_key', None).encode('UTF-8')
    industry = request.form.get('industry', None).encode('UTF-8')
    role = request.form.get('role', None).encode("UTF-8")

    page = request.form.get('page', None)
    count_of_page = request.form.get('count_of_page', None)

    r = GroupRecordModel.get_all_card_in_a_group(group_token, int(page), int(count_of_page), search_key, industry, role)
    group_data = GroupLinksModel.get_group_message_by_token(group_token)
    r['group_data'] = group_data
    response = make_response(json.dumps(r))
    response.headers['Content-Type'] = 'application/json'
    return response


@api_app.route('get_own_message')
@login_handle
def get_own_message():
    """
    获取自己的消息列表
    :return:
    """
    objs = ChatModel.get_last_chat_message(g.open_id)
    response = make_response(json.dumps(objs))
    response.headers['Content-Type'] = 'application/json'
    return response


@api_app.route('get_card_of_a_prople/<open_id>')
@login_handle
def get_card_of_a_prople(open_id):
    """
    获取某位用户的信息
    :param open_id: 用户openid
    :return:
    """

    if not BusinessCardModel.has_card(open_id):
        return abort(404)

    card = BusinessCardModel.get_name_card(open_id)
    card = BusinessCardModel.handle_data_use_in_json(card)

    if card['redundancy_labels']:
        card['keys'] = card['redundancy_labels'].split('#')
    else:
        card['keys'] = []

    if FriendModel.is_friend(g.open_id, open_id) or open_id == g.open_id:
        card['is_friend'] = 0
    else:
        card['is_friend'] = 1

    # 判断是不是自己
    if open_id == g.open_id:
        card['is_me'] = 0
    else:
        card['is_me'] = 1

    response = make_response(json.dumps(card))
    response.headers['Content-Type'] = 'application/json'
    return response


@api_app.route('get_chat_need_message', methods=['POST'])
@login_handle
def get_chat_need_message():
    """
    获取聊天页面初始化信息
    :return:
    """

    friend_open_id = request.form.get('friend_open_id', None)

    own_card = BusinessCardModel.get_name_card(g.open_id)
    own_card = BusinessCardModel.handle_data_use_in_json(own_card)
    friend_card = BusinessCardModel.get_name_card(friend_open_id)
    friend_card = BusinessCardModel.handle_data_use_in_json(friend_card)
    obj = {"own_card": own_card, "friend_card": friend_card}

    title = friend_card['name']

    r = {'own_card': own_card, 'title': title, 'obj': obj}

    response = make_response(json.dumps(r))
    response.headers['Content-Type'] = 'application/json'
    return response


@api_app.route('get_own_new_message_number')
@login_handle
def get_own_new_message_number():
    """
    获取自己的未读消息数
    :return:
    """
    nums = ChatModel.get_all_not_read_message_number(g.open_id)
    nums2 = ResourceHelperMessageModel.get_not_read_message_number(g.open_id)
    response = make_response(json.dumps({"nums": nums + nums2}))
    response.headers['Content-Type'] = 'application/json'
    return response


@api_app.route('apply_friend', methods=['POST'])
@login_handle
def apply_friend():
    """
    申请添加好友
    :return:
    """
    source_open_id = g.open_id
    target_open_id = request.form.get('target_open_id', None)
    remarks = request.form.get('remarks', None)

    if not BusinessCardModel.has_card(target_open_id) or not BusinessCardModel.has_card(source_open_id):
        return abort(404)

    r = ApplyFriendsModel.apply_friend(source_open_id, target_open_id, remarks)
    response = make_response(json.dumps({"r": r}))
    response.headers['Content-Type'] = 'application/json'
    return response


@api_app.route('handle_apply_friend/<int:apply_id>/<int:handle_status>')
@login_handle
def handle_apply_friend(apply_id, handle_status):
    """
    处理添加好友信息
    :return:
    """

    apply_obj = ApplyFriendsModel.find_by_id(apply_id)

    # 检查申请是否属于自己
    if apply_obj['target_open_id'] != g.open_id:
        return abort(404)

    # 检查信息是否已经处理
    if apply_obj['status'] == 0:
        if handle_status == 1:
            FriendModel.add_friend(apply_obj['source_open_id'], apply_obj['target_open_id'])
        # 标志申请已经处理
        ApplyFriendsModel.handle_apply(apply_id, handle_status, g.open_id)
        r = {"code": 0}
    else:
        r = {"code": -1}

    response = make_response(json.dumps(r))
    response.headers['Content-Type'] = 'application/json'
    return response


@api_app.route('get_new_resource_message')
@login_handle
def get_new_resource_message():
    """
    获取最新资源小助手信息
    :return:
    """
    objs = ResourceHelperMessageModel.get_new_message(g.open_id)
    return make_a_data(objs)


@api_app.route('send_resource_message', methods=['POST'])
@login_handle
def send_resource_message():
    """
    发送消息给资源小助手
    :return:
    """
    message = request.form.get('message', None)
    ResourceHelperMessageModel.add_message(1, g.open_id, '', message, 0)
    return make_a_data(0)


@api_app.route('get_a_page_of_resource', methods=['POST'])
@login_handle
def get_a_page_of_resource():
    """
    获取一页资源小助手信息
    :return:
    """
    page = request.form.get('page', None)
    count_of_page = request.form.get('count_of_page', None)
    last_message_id = request.form.get('last_message_id', None)

    if not int(last_message_id):
        last_message_id = None

    r = ResourceHelperMessageModel.get_old_message_from_user(g.open_id, int(page), int(count_of_page), last_message_id)
    return make_a_data(r)
