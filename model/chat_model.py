# coding:UTF-8


"""
聊天记录模型
@author: yubang
2016.03.02
"""

from model.base_model import BaseModel
from model.business_card import BusinessCardModel


class ChatModel(BaseModel):
    db_lib = BaseModel.get_db_lib()
    table_name = 'card_chats'

    @classmethod
    def send_message(cls, from_open_id, to_open_id, message, message_type):
        """
        发送一条消息
        :param from_open_id: 发送方openid
        :param to_open_id: 接收方openid
        :param message: 消息内容
        :param message_type: 消息类型，0为文字
        :return:
        """

        # 判断目标用户是否存在
        if not BusinessCardModel.has_card(to_open_id) or from_open_id == to_open_id:
            return 0

        sql = "insert into " + cls.table_name + "(from_open_id, to_open_id, message_content, message_type, status, " \
                                                "create_time) values(%s, %s, %s, %s, 0, now());"
        r = cls.db_lib.insert(sql, [from_open_id, to_open_id, message, message_type])
        return r

    @classmethod
    def get_a_page_of_chats(cls, open_id, friend_open_id, page, number_of_page):
        """
        获取一页聊天记录
        :param open_id: 用户openid
        :param friend_open_id: 好友openid
        :param page: 页数
        :param number_of_page: 每页记录数
        :return:
        """
        index = (page - 1) * number_of_page
        sql = "select * from " + cls.table_name + " where (from_open_id = %s AND to_open_id = %s) or (from_open_id = %s AND to_open_id = %s) order by id desc limit " + str(index) + \
              "," + str(number_of_page)
        return cls.db_lib.query_for_list(sql, [friend_open_id, open_id, open_id, friend_open_id])

    @classmethod
    def get_all_new_message(cls, open_id, friend_open_id):
        """
        获取所有未读消息
        :param open_id: 用户openid
        :param friend_open_id: 好友openid
        :return:
        """
        sql = "select * from " + cls.table_name + " where from_open_id = %s AND to_open_id = %s AND status = 0;"
        messages = cls.db_lib.query_for_list(sql, [friend_open_id, open_id])

        # 标志消息已阅读
        message_ids = []
        for obj in messages:
            message_ids.append(obj['id'])
        cls.__sign_read_new_message(message_ids)

        return messages

    @classmethod
    def __sign_read_new_message(cls, message_ids):
        """
        标识新消息已经阅读
        :param message_ids: 消息id列表
        :return:
        """
        if not message_ids:
            return

        string = ','.join(map(lambda x: str(x), message_ids))
        string = '(' + string + ')'
        sql = "update " + cls.table_name + " set status = 1 where id in " + string
        cls.db_lib.update(sql, [])

    @classmethod
    def get_message_number(cls, open_id, friend_open_id):
        """
        获取聊天记录数量和未读消息数量
        :param open_id: 用户openid
        :param friend_open_id: 好友openid
        :return: 未读消息书， 总消息数
        """

        sql = "select count(*) as nums from " + cls.table_name + " where from_open_id = %s AND to_open_id = %s limit 1;"
        all_number = cls.db_lib.query_for_dict(sql, [friend_open_id, open_id]).get('nums', 0)

        sql = "select count(*) as nums from " + cls.table_name + " where from_open_id = %s AND to_open_id = %s AND " \
                                                                 "status = 0 limit 1;"
        new_number = cls.db_lib.query_for_dict(sql, [friend_open_id, open_id]).get('nums', 0)

        return new_number, all_number
