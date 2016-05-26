# coding:UTF-8


"""
输出数据处理
@author: yubang
2016.03.08
"""


from flask import make_response
import json

code_message = {
    0: 'ok',
    1: u'用户未登录',
    2: u'跳转链接',
    3: u'降级处理',
    4: u'服务器内部错误',
    5: u'没权限访问',
    6: u'服务器拒绝请求',
    7: u'请求参数缺失',
    8: u'请求数据非法',
    9: u'请求次数过多',
    10: u'API身份校验出错',
}


def make_a_data(data, code=0, sleep=5, sleep_tip='', jump_address=''):
    """
    封装返回类
    :param data: 自定义数据
    :param code: 状态码
    :param sleep: 延迟访问时间
    :param sleep_tip: 延迟访问提示
    :param jump_address: 跳转地址
    :return: response对象
    """
    r = {"code": code, "msg": code_message[code], "content": data}

    if code == 2:
        r['jump_address'] = jump_address
    elif code == 3:
        r['sleep'] = sleep
        r['sleep_tip'] = sleep_tip

    response = make_response(json.dumps(r))
    response.headers['Content-Type'] = 'application/json'
    return response
