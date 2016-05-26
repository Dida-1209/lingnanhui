# coding:UTF-8

"""
资源小助手模型
@author: yubang
2016.04.02
"""


from model.base_model import BaseModel
from lib.redis_lib import redis_client
from dao.all_model import model_manager
from MySQLdb import escape_string
import datetime


class ResourceHelperMessageModel(BaseModel):
    table_name = 'card_resource_helper_message'
    db = BaseModel.get_db_lib()

    @classmethod
    def add_message(cls, send_or_receive, source_open_id, target_open_id, message_content, status):
        """
        添加一条信息
        :param send_or_receive: 0为发送，1为接收信息
        :param source_open_id: 发送方人群，空字符串为资源小助手
        :param target_open_id: 目标用户openid，空字符串为全台成员
        :param message_content: 消息内容
        :param status: 0为正常，1为删除
        :return: 消息id
        """

        if type(status) != int:
            raise Exception('args type error!')

        status = str(status)
        create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = "insert into " + cls.table_name + "(send_or_receive, source_open_id, target_open_id, message_content, status, create_time) values(%s, %s, %s, %s, %s, %s);"
        return cls.db.insert(sql, [send_or_receive, source_open_id, target_open_id, message_content, status, create_time])

    @classmethod
    def get_not_read_message_number(cls, open_id):
        """
        获取用户未读消息数
        :param open_id: 用户openid
        :return:
        """
        cache_key = 'sign_resource_helper_' + open_id

        # 获取最后一次读取时间
        last_read_time = redis_client.get(cache_key)
        if not last_read_time:
            last_read_time = model_manager['BusinessCardModel'].get_user_create_time(open_id)

        sql = "select count(*) as nums from "+cls.table_name+" where send_or_receive = 0 AND (target_open_id = '' OR target_open_id = %s) AND create_time > %s  AND status = 0 limit 1;"

        obj = cls.db.query_for_dict(sql, [open_id, last_read_time])
        return obj['nums']

    @classmethod
    def get_new_message(cls, open_id):
        """
        获取最新未读消息
        :param open_id: 用户openid
        :return:
        """

        cache_key = 'sign_resource_helper_' + open_id

        # 获取最后一次读取时间
        last_read_time = redis_client.get(cache_key)
        if not last_read_time:
            last_read_time = model_manager['BusinessCardModel'].get_user_create_time(open_id)

        # 记录下当前阅读时间
        redis_client.set(cache_key, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        sql = "select * from "+cls.table_name+" where send_or_receive = 0 AND (target_open_id = '' OR target_open_id = %s) AND create_time >= %s AND status = 0;"

        objs = cls.db.query_for_list(sql, [open_id, last_read_time])
        objs = map(cls.handle_data_use_in_json, objs)
        return objs

    @classmethod
    def get_resource_helper_message_of_page(cls, page, count_of_page):
        """
        获取一页信息
        :param page: 页数
        :param count_of_page: 每页记录数
        :return:
        """
        return cls.get_one_page_of_table(cls.table_name, "status = 0", page, count_of_page, order_by='create_time desc')

    @classmethod
    def remove_message(cls, message_id):
        """
        删除信息
        :param message_id: 信息id
        :return:
        """
        sql = "update " + cls.table_name + " set status = 1 where id = %d;" % (message_id)
        return cls.db.update(sql)

    @classmethod
    def get_old_message_from_user(cls, open_id, page, count_of_page, last_message_id=None):
        """
        获取一页资源小助手信息
        :param open_id: 用户openid
        :param page: 页数
        :param count_of_page: 每页记录数
        :param last_message_id:  在那条记录之前
        :return:
        """

        cache_key = 'sign_resource_helper_' + open_id
        # 记录下当前阅读时间
        redis_client.set(cache_key, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        able_look_time = model_manager['BusinessCardModel'].get_user_create_time(open_id)
        if not able_look_time:
            able_look_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        open_id = escape_string(open_id)
        where_str = "(((target_open_id = '%s' OR target_open_id = '') AND send_or_receive = 0) OR (source_open_id = '%s') ) AND create_time >= '%s' AND status = 0" % (open_id, open_id, able_look_time)

        if last_message_id is not None:
            where_str += (" AND id < %d" % int(last_message_id))

        return cls.get_one_page_of_table(cls.table_name, where_str, page, count_of_page, order_by="create_time desc")

    @classmethod
    def get_last_message(cls, open_id):
        """
        获取最近一条消息
        :param open_id: 用户openid
        :return:
        """
        able_look_time = model_manager['BusinessCardModel'].get_user_create_time(open_id)
        if not able_look_time:
            able_look_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sql = "select * from " + cls.table_name + " where (((target_open_id = %s OR target_open_id = '') AND send_or_receive = 0) OR (source_open_id = %s) ) AND create_time >= %s  AND status = 0 order by create_time desc limit 1;"
        return cls.db.query_for_dict(sql, [open_id, open_id, able_look_time])
