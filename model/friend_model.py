# coding:UTF-8


"""
好友关系模型
@author: yubang
2016.02.29
"""


from model.base_model import BaseModel
from model.business_card import BusinessCardModel


class FriendModel(BaseModel):
    @classmethod
    def get_table_name(cls):
        return "card_friends"

    @classmethod
    def is_friend(cls, source_open_id, target_open_id):
        """
        判断两个用户是不是好友
        :param source_open_id: 用户1openid
        :param target_open_id: 用户2openid
        :return: boolean
        """
        sql = "select count(*) as nums from " + cls.get_table_name() + " where source_open_id = %s AND target_open_id = " \
                                                                       "%s AND status = 0 limit 1;"
        db_lib = cls.get_db_lib()
        obj = db_lib.query_for_dict(sql, [source_open_id, target_open_id])

        return obj['nums'] != 0

    @classmethod
    def add_friend(cls, source_open_id, target_open_id):
        """
        添加好友
        :param source_open_id: 用户1openid
        :param target_open_id: 用户2openid
        :return: boolean
        """

        if cls.is_friend(source_open_id, target_open_id):
            return False

        if not BusinessCardModel.has_card(target_open_id):
            return False

        if source_open_id == target_open_id:
            return False

        sql = "insert into " + cls.get_table_name() + "(source_open_id, target_open_id, status, create_time) " \
                                                      "values(%s, %s, 0, now());"
        db_lib = cls.get_db_lib()
        db_lib.insert(sql, [source_open_id, target_open_id])
        db_lib.insert(sql, [target_open_id, source_open_id])
        return True

    @classmethod
    def get_all_friends(cls, open_id):
        """
        获取用户所有好友
        :param open_id: 用户id
        :return:
        """
        t = " %s as A, %s as B " % (cls.get_table_name(), BusinessCardModel.get_table_name())
        sql = "select B.name, B.company, B.open_id, B.avatar, B.industry, B.name_pinyin from " + t + " where A.source_open_id = %s AND A.status = 0 AND A.target_open_id = B.open_id order by B.name asc;"
        db_lib = cls.get_db_lib()
        objs = db_lib.query_for_list(sql, [open_id])
        return objs
