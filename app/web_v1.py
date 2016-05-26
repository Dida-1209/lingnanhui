# coding:UTF-8


"""
静态页面模块
@author: yubang
2016.03.13
"""


from flask import Blueprint, render_template, g
from model.business_card import BusinessCardModel
from app.api import login_handle


web_app = Blueprint('web_app', __name__)


@web_app.route('chat/<friend_open_id>')
@login_handle
def chat_html(friend_open_id):
    """
    聊天页面
    :param friend_open_id: 好友openid
    :return:
    """

    own_card = BusinessCardModel.get_name_card(g.open_id)
    friend_card = BusinessCardModel.get_name_card(friend_open_id)
    obj = {"own_card": own_card, "friend_card": friend_card}

    title = friend_card['name']

    return render_template("v1/chat.html", title=title, friend_open_id=friend_open_id, obj=obj)


@web_app.route('contact_list')
@login_handle
def contact_list():
    """
    联系人列表
    :return:
    """
    return render_template("v1/contact_list.html")
