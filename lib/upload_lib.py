# coding:UTF-8


"""
上传文件封装
"""

from qiniu import Auth, put_data
from config import other_config
import hashlib


def upload_file(data):
    """
    上传文件
    :param data: data文件数据
    :return:
    """
    key = other_config.prefix + hashlib.md5(data).hexdigest()

    q = Auth(other_config.access_key, other_config.secret_key)
    token = q.upload_token(other_config.bucket_name)
    put_data(token, key, data)

    return other_config.url + key
