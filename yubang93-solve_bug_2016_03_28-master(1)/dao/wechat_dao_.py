# coding:UTF-8

"""
这个类要注意，都是跟微信开发沾边了，调试特别难
@author: yubang
2016.04.08
"""

from lib.logging_lib import log
import requests


def tell_api_build_card(open_id, pic_url):
    """
    告诉API接口，我们生成了一张海报
    :return:
    """
    r = requests.post('http://wechatsys.lingnanchuangye.com/set_key_data/frefer45g4re514re', data={
        'key': 'poster_image_' + open_id,
        'value': pic_url
    })
    if r.status_code != 200:
        log.error(u'通知微信公众号生成了新海报操作失败，用户openid：%s' % open_id)
        raise Exception('error!')
