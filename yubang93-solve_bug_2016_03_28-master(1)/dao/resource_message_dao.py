# coding:UTF-8


"""
发送信息通过资源小助手
@author: yubang
2016.04.03
"""

from dao.all_model import model_manager
from lib.tools import html_change_to_png
from dao.wechat_dao_ import tell_api_build_card
from dao import other_dao
from lib.logging_lib import log
import cgi


def __send_message_use_api(target_open_id, message_content):
    model_manager['ResourceHelperMessageModel'].add_message(0, '', target_open_id, message_content, 0)


def __send_poster(open_id, poster_url):
    pic_url = html_change_to_png(poster_url)
    if pic_url is None:
        # __send_message_use_api(open_id, u'生成个人海报失败，请向我们反馈！')
        log.error(u'生成个人海报失败，用户openid：%s' % open_id)
        return None
    content = "<img style='width: 200px;' src='%s'>" % pic_url
    __send_message_use_api(open_id, content)

    # 告诉微信自动回复系统名片海报已经更新
    tell_api_build_card(open_id, pic_url)


@other_dao.celery_obj_dao.task
def send_welcome_message(open_id, poster_url):
    """
    发送欢迎信息给用户，新建名片之后
    :param open_id: 用户openid
    :return:
    """
    content = u"点击名片，保存你的名片，然后分享给好友可邀请他的资源共享到你的资源库，多收集好友资源，对你事业有又很大的帮助，在你需要的时候可直接在自己资源库检索。"
    __send_message_use_api(open_id, content)

    # 发送海报
    __send_poster(open_id, poster_url)


@other_dao.celery_obj_dao.task
def send_poster(open_id, poster_url):
    """
    发送海报图片给用户
    :param open_id:用户openid
    :return:
    """
    __send_poster(open_id, poster_url)


@other_dao.celery_obj_dao.task
def commit_apply(source_open_id, target_open_id, message_id):
    """
    提交申请的时候发送消息
    :param source_open_id: 源用户openid
    :param target_open_id: 目标用户openid
    :return:
    """

    source_card = model_manager['BusinessCardModel'].get_name_card(source_open_id)
    target_card = model_manager['BusinessCardModel'].get_name_card(target_open_id)
    message_data = model_manager['ApplyFriendsModel'].find_by_id(message_id)

    if source_card['redundancy_labels']:
        source_card['keys'] = source_card['redundancy_labels'].split("#")
        if len(source_card['keys']) > 2:
            source_card['keys'] = source_card['keys'][:2]
    else:
        source_card['keys'] = []

    # 发送给申请者的
    content = u"您的申请已发送出去"
    __send_message_use_api(source_open_id, content)

    # 发送给被申请者的

    #
    # xxx申请与你资源对接，他有xx和xx（资源标签，只放两个）等资源，是否同意。
    # 他的备注：XXX
    #

    content = u"""
        %s申请与你资源对接，他有%s等资源，是否同意。<br>
        他的备注：%s<br>
        <font style='color:blue;'><a href='javascript:handle_apply_in_chat(%d,1);'>同意</></font><br>
        <font style='color:blue;'><a href='javascript:handle_apply_in_chat(%d,2);'>不同意</a></font><br>
    """ % (source_card['name'], u'和'.join(source_card['keys']), cgi.escape(message_data['remarks']), message_id, message_id)
    __send_message_use_api(target_open_id, content)


@other_dao.celery_obj_dao.task
def handle_apply(apply_id, handle_status):
    """
    处理申请
    :param apply_id: 申请id
    :param handle_status: 处理状态
    :return:
    """
    apply_data = model_manager['ApplyFriendsModel'].find_by_id(apply_id)
    card = model_manager['BusinessCardModel'].get_name_card(apply_data['target_open_id'])
    if handle_status == 1:
        content = u'%s已通过你的申请' % card['name']
    else:
        content = u'%s已拒绝你的申请' % card['name']

    __send_message_use_api(apply_data['source_open_id'], content)
