# coding:UTF-8

"""
微信群自动回复配置表
@author: yubang
2016.03.10
"""

from model.base_model import BaseModel


class WechatReplyModel(BaseModel):
    table_name = "topic_wechat_reply"
    db = BaseModel.get_db_lib()

    @classmethod
    def add_setting(cls, wechat_group_name, reply_content, status, reply_key):
        """
        添加机器人绑定
        :param wechat_group_name: 微信群昵称
        :param reply_content: 自动回复内容
        :param status: 回复状态
        :param reply_key: 回复关键字
        :return:
        """
        sql = "insert into " + cls.table_name + "(wechat_group_name, reply_content, status, create_time, reply_key) values(%s, %s, %s, now(), %s);"
        return cls.db.insert(sql, [wechat_group_name, reply_content, str(status), reply_key])

    @classmethod
    def update_setting(cls, wechat_group_name, reply_content, status, reply_id, reply_key):
        """
        修改自动回复配置
        :param wechat_group_name: 微信群昵称
        :param reply_content: 自动回复内容
        :param reply_id: 主键id
        :param status: 回复状态
        :param reply_key: 回复关键字
        :return:
        """
        sql = "update " + cls.table_name + " set wechat_group_name = %s, reply_content = %s, status = %s, reply_key = %s where id = %s;"
        return cls.db.update(sql, [wechat_group_name, reply_content, str(status), reply_key, reply_id])

    @classmethod
    def remove_setting(cls, reply_id):
        """
        删除配置
        :param reply_id: 主键id
        :return:
        """
        sql = "update " + cls.table_name + " set status = 2 where id = %s;"
        return cls.db.update(sql, [reply_id])

    @classmethod
    def get_replys(cls):
        """
        获取自动回复配置
        :return:
        """
        sql = "select * from " + cls.table_name + " where status < 2 order by create_time;"
        return cls.db.query_for_list(sql)
