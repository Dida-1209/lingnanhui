# coding:UTF-8


"""
群链接模型
@author: yubang
2016.03.30
"""


from model.base_model import BaseModel
import time
import hashlib


class GroupLinksModel(BaseModel):
    table_name = 'card_group_links'
    db = BaseModel.get_db_lib()

    @classmethod
    def has_link(cls, group_token):
        """
        判断是否有这个链接
        :param group_token: 群凭证
        :return: boolean
        """
        sql = "select count(*) as nums from " + cls.table_name + " where group_token = %s AND group_status = 0 limit 1;"
        obj = cls.db.query_for_dict(sql, [group_token])
        return obj['nums'] != 0

    @classmethod
    def add_link(cls, group_title, group_status):
        """
        新增一条群链接
        :param group_title: 群名字
        :param group_status: 群状态
        :return: 链接id
        """
        group_token = hashlib.md5(str(time.time())).hexdigest()
        sql = "insert into " + cls.table_name + " (group_title, group_token, group_status, create_time) values(%s, %s, %s, now());"
        return cls.db.insert(sql, [group_title, group_token, group_status])

    @classmethod
    def update_link(cls, group_title, group_status, group_token):
        """
        修改一条群链接
        :param group_title: 群名字
        :param group_status: 群状态
        :return: boolean
        """
        sql = "update " + cls.table_name + " set group_title = %s, group_status = %s where group_token = %s;"
        return cls.db.update(sql, [group_title, group_status, group_token])

    @classmethod
    def get_a_page_of_link(cls, page, count_of_page):
        """
        获取一页链接
        :param page: 第几页
        :param count_of_page: 每页记录数
        :return:
        """
        return BaseModel.get_one_page_of_table(cls.table_name, " group_status = 0 or group_status = 1", page, count_of_page)

    @classmethod
    def remove_link(cls, group_token):
        """
        删除一条链接
        :param group_token: 群凭证
        :return: boolean
        """
        sql = "update " + cls.table_name + " set group_status = 2 where group_token = %s;"
        return cls.db.update(sql, [group_token]) != 0

    @classmethod
    def get_group_message_by_token(cls, group_token):
        """
        获取链接信息
        :param group_token:
        :return:
        """
        sql = "select * from " + cls.table_name + " where group_token = %s AND group_status = 0 limit 1;"
        obj = cls.db.query_for_dict(sql, [group_token])
        return cls.handle_data_use_in_json(obj)
