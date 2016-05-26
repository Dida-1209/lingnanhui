# coding:UTF-8


"""
数据库模型基类
"""

from lib import db_lib


class BaseModel(object):
    @classmethod
    def get_db_lib(cls):
        return db_lib

    @classmethod
    def handle_data_use_in_json(cls, obj):
        if 'create_time' in obj:
            obj['create_time'] = obj['create_time'].strftime("%Y-%m-%d %H:%M:%S")
        if 'update_time' in obj:
            obj['update_time'] = obj['update_time'].strftime("%Y-%m-%d %H:%M:%S")
        return obj
