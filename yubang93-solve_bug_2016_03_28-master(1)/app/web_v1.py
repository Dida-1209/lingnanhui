# coding:UTF-8


"""
静态页面模块
@author: yubang
2016.03.13
"""


from flask import Blueprint, render_template, g, abort, url_for, request, session, redirect, send_file
from model.business_card import BusinessCardModel
from functools import wraps
from model.apply_friends import ApplyFriendsModel
from app.api import login_handle
from model.group_links_model import GroupLinksModel
from model.group_record import GroupRecordModel
from lib.logging_lib import log
import urllib


web_app = Blueprint('web_app', __name__)


def must_has_own_card(fn):
    """
    处理必须拥有名片的情况
    :param fn:
    :return:
    """
    @wraps(fn)
    def handle(*k, **v):
        if not BusinessCardModel.has_card(g.open_id):
            return redirect(url_for('web_app.build_card'))
        return fn(*k, **v)
    return handle


@web_app.route('chat/<friend_open_id>')
@login_handle
@must_has_own_card
def chat_html(friend_open_id):
    """
    聊天页面
    :param friend_open_id: 好友openid
    :return:
    """
    return send_file("templates/v1/chat.html", cache_timeout=0)


@web_app.route('contact_list')
@login_handle
@must_has_own_card
def contact_list():
    """
    联系人列表
    :return:
    """
    return send_file("templates/v1/contact_list.html", cache_timeout=0)


@web_app.route('main_card_list')
@login_handle
@must_has_own_card
def main_card_list():
    """
    名片列表
    :return:
    """
    return send_file("templates/v1/main_card_list.html", cache_timeout=0)


@web_app.route('card/<open_id>')
@login_handle
@must_has_own_card
def card(open_id):
    """
    获取个人名片
    :param open_id: 名片openid
    :return:
    """
    card = BusinessCardModel.get_name_card(open_id)

    if not card:
        return abort(404)

    url = url_for("api.add_friend", _external=True, friend_open_id=open_id)
    url = urllib.quote(url)

    if card['redundancy_labels']:
        card['keys'] = card['redundancy_labels'].split('#')
    else:
        card['keys'] = []
    return render_template('v1/card.html', card=card, url=url)


@web_app.route('search_card')
@login_handle
@must_has_own_card
def search_card():
    """
    搜索名片结果页面
    :return:
    """

    search_key = request.args.get('search_key', None)
    industry = request.args.get('industry', None)
    role = request.args.get('role', None)

    if search_key is None or industry is None or role is None:
        return abort(404)

    return send_file('templates/v1/search_card.html', cache_timeout=0)


@web_app.route('people/<open_id>')
@login_handle
@must_has_own_card
def people(open_id):
    """
    联系人列表
    :param open_id: 用户openid
    :return:
    """
    if not BusinessCardModel.has_card(open_id):
        return abort(404)

    return send_file('templates/v1/people.html', cache_timeout=0)


@web_app.route('message')
@login_handle
@must_has_own_card
def message():
    """
    获取消息列表
    :return:
    """

    return send_file('templates/v1/message.html', cache_timeout=0)


@web_app.route('buildCard')
@login_handle
def build_card():
    """
    生成名片页面
    :return:
    """

    if BusinessCardModel.has_card(g.open_id):
        return redirect(url_for('web_app.update_card'))

    g.target_url = '/api/v1/generatedNameCard'
    return send_file('templates/v1/build_card.html', cache_timeout=0)


@web_app.route('updateCard')
@login_handle
@must_has_own_card
def update_card():
    """
    修改名片页面
    :return:
    """

    if not BusinessCardModel.has_card(g.open_id):
        return redirect(url_for('web_app.build_card'))

    card = BusinessCardModel.get_name_card(g.open_id)
    g.target_url = '/api/v1/updateNameCard'
    return send_file('templates/v1/build_card.html', cache_timeout=0)


@web_app.route('to_wechat_link/<group_token>')
@login_handle
def to_wechat_link(group_token):
    """
    微信群的链接
    :return:
    """
    if not GroupLinksModel.has_link(group_token):
        return abort(404)

    session['group_token'] = group_token

    if BusinessCardModel.has_card(g.open_id):

        # 判断是否要添加入群
        if not GroupRecordModel.has_join_group(g.open_id, group_token):
            GroupRecordModel.join_group(g.open_id, group_token)
            log.info(u'%s执行了记录加入群的数据库操作' % g.open_id)
        log.info(u'%s点击了群链接' % g.open_id)
        return redirect(url_for('web_app.all_cards', group_token=group_token))
    else:
        return redirect(url_for('web_app.build_card') + "?group_token="+group_token)


@web_app.route('all_cards/<group_token>')
@login_handle
@must_has_own_card
def all_cards(group_token):
    """
    所有名片页面
    :return:
    """

    if not GroupLinksModel.has_link(group_token):
        return abort(404)

    return send_file('templates/v1/all_cards.html', cache_timeout=0)


@web_app.route('code_share')
@login_handle
def code_share():
    """
    二维码分享页面
    :return:
    """
    return send_file('templates/v1/code_share.html', cache_timeout=0)


@web_app.route('apply_friend')
@login_handle
@must_has_own_card
def apply_friend():
    """
    申请添加好友页面
    :return:
    """
    target_open_id = request.args.get('open_id', None)
    source_open_id = g.open_id
    if not BusinessCardModel.has_card(target_open_id) or not BusinessCardModel.has_card(source_open_id):
        return abort(404)

    return send_file('templates/v1/apply_friend.html', cache_timeout=0)


@web_app.route('poster/<open_id>')
def poster(open_id):
    """
    用户海报页面
    （注意，该页面不需要登录校验～～～～）
    :return:
    """
    if not BusinessCardModel.has_card(open_id):
        return abort(404)

    card = BusinessCardModel.get_name_card(open_id)

    if card['redundancy_labels']:
        card['keys'] = card['redundancy_labels'].split('#')
        # 只取前5个
        if len(card['keys']) > 5:
            card['keys'] = card['keys'][:5]
    else:
        card['keys'] = []

    # 生成二维码地址
    url = url_for('web_app.join_card_by_user_code', _external=True)+ "?from_open_id=" + card['open_id'] + "&invitation_code=" + card['invitation_code']
    card['url'] = urllib.quote(url)

    return render_template('v1/poster.html', card=card)


@web_app.route('join_card_by_user_code')
@login_handle
def join_card_by_user_code():
    """
    扫描二维码跳转页面
    :return:
    """

    # 由于该页面是一个主入口，逻辑处理需要严谨

    # 必须参数，from_open_id： 来源用户，invitation_code：邀请码
    from_open_id = request.args.get('from_open_id', None)
    invitation_code = request.args.get('invitation_code', None)
    if from_open_id is None or invitation_code is None:
        return abort(404)

    # 检查来源用户是否存在
    if not BusinessCardModel.has_card(from_open_id):
        return abort(404)

    # 检查邀请码？？？（暂时忽略）
    pass

    # 如果是自己扫描自己的二维码，就什么都不处理，跳转到资源社区主页
    if g.open_id == from_open_id:
        return redirect(url_for('web_app.contact_list'))

    # 用户已经生成名片，发送申请资源请求，跳转到资源社区主页
    if BusinessCardModel.has_card(g.open_id):
        ApplyFriendsModel.apply_friend(g.open_id, from_open_id, u'通过扫描您的海报申请资源对接')
        return redirect(url_for('web_app.contact_list'))

    # 用户还没有生成名片，跳转到生成名片页面
    return redirect(url_for('web_app.build_card') + "?from_open_id=" + from_open_id + "&invitation_code=" + invitation_code)


@web_app.route('resource_html')
@login_handle
@must_has_own_card
def resource_html():
    """
    资源小助手聊天页面
    :return:
    """
    return send_file('templates/v1/resource_html.html', cache_timeout=0)


@web_app.route('customer_code')
def customer_code():
    """
    客服二维码页面
    :return:
    """
    return send_file('templates/v1/customer_code.html', cache_timeout=0)
