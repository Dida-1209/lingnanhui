# coding:UTF-8


"""
小工具箱
@author: yubang
2016.04.03
"""

import requests


def html_change_to_png(web_url):
    """
    网页转成图片
    :param web_url: 网页地址
    :return: 图片地址
    """
    data = {"token": 'FREFERdiehjuerhufrei4545greFREFERfgg?%$&&btgrb', 'web_url': web_url, 'width': 414, 'height': 736, 'pic_type': 'jpg'}
    response = requests.post('http://htmlpic.lingnanchuangye.com/html_to_png/abc123ABC', data)
    if response.status_code != 200:
        return None
    return response.text
