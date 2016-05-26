# coding:UTF-8


"""
聊天记录模型
@author: yubang
2016.03.02
"""

from model.base_model import BaseModel
from model.business_card import BusinessCardModel
from dao.all_model import model_manager


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
        if not BusinessCardModel.has_card(to_open_id):
            return 0

        sql = "insert into " + cls.table_name + "(from_open_id, to_open_id, message_content, message_type, status, " \
                                                "create_time) values(%s, %s, %s, %s, 0, now());"
        r = cls.db_lib.insert(sql, [from_open_id, to_open_id, message, message_type])
        return r

    @classmethod
    def get_a_page_of_chats(cls, open_id, friend_open_id, page, number_of_page, last_message_id):
        """
        获取一页聊天记录
        :param open_id: 用户openid
        :param friend_open_id: 好友openid
        :param page: 页数
        :param number_of_page: 每页记录数
        :param last_message_id: 最后一条阅读消息id
        :return:
        """

        if last_message_id:
            limit_by_id = ' AND id < %d ' % last_message_id
        else:
            limit_by_id = ''

        index = (page - 1) * number_of_page
        sql = "select * from " + cls.table_name + " where ((from_open_id = %s AND to_open_id = %s) or (from_open_id = %s AND to_open_id = %s)) " + limit_by_id + " order by id desc limit " + str(index) + \
              "," + str(number_of_page)
        objs = cls.db_lib.query_for_list(sql, [friend_open_id, open_id, open_id, friend_open_id])

        ids = []
        for obj in objs:
            if obj['status'] == 0 and obj['to_open_id'] == open_id:
                ids.append(obj['id'])
        cls.__sign_read_new_message(ids)
        return objs

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
            if obj['to_open_id'] == open_id:
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

    @classmethod
    def get_last_chat_message(cls, open_id):
        """
        获取最后一条联系人信息
        :param open_id:
        :return:
        """
        temp_str = "(select * from %s order by create_time desc) temp_table" % cls.table_name
        sql = "select * from " + temp_str + " where to_open_id = %s group by from_open_id order by create_time desc"
        objs = cls.get_db_lib().query_for_list(sql, [open_id])

        r = list()
        for obj in objs:
            r.append(obj)

        sql = "select * from " + temp_str + " where from_open_id = %s group by to_open_id"
        objs = cls.get_db_lib().query_for_list(sql, [open_id])
        new_objs = []

        for obj in objs:
            index = 0
            exist_sign = False
            while index < len(r):
                if obj['to_open_id'] == r[index]['from_open_id']:
                    if obj['create_time'].now() > r[index]['create_time'].now():
                        r[index] = obj
                    exist_sign = True
                    break
                index += 1
            if not exist_sign:
                new_objs.append(obj)

        r.extend(new_objs)

        # 填充联系人信息
        index = 0
        while index < len(r):

            if r[index]['to_open_id'] != open_id:
                r[index]['user'] = BusinessCardModel.get_name_card(r[index]['to_open_id'])
            else:
                r[index]['user'] = BusinessCardModel.get_name_card(r[index]['from_open_id'])

            r[index]['user'] = BusinessCardModel.handle_data_use_in_json(r[index]['user'])
            r[index]['message_nums'] = cls.get_message_number(open_id, r[index]['user']['open_id'])

            index += 1

        # 特殊处理资源小助手
        reource_obj = model_manager['ResourceHelperMessageModel'].get_last_message(open_id)
        if reource_obj:
            reource_obj['user'] = {'name': u'资源小助手', "avatar": '/static/v1/img/webwxgetmsgimg.jpg', 'open_id': ''}
            reource_obj['message_nums'] = (model_manager['ResourceHelperMessageModel'].get_not_read_message_number(open_id), 0)

            r.append(reource_obj)

        # 按时间排序
        i = 0
        while i < len(r):
            j = i + 1
            while j < len(r):
                if r[i]['create_time'] < r[j]['create_time']:
                    temp_obj = r[i]
                    r[i] = r[j]
                    r[j] = temp_obj
                j += 1
            i += 1

        r = map(cls.handle_data_use_in_json, r)

        return r

    @classmethod
    def get_all_not_read_message_number(cls, open_id):
        """
        获取所有未读消息数
        :param open_id: 用户openid
        :return:
        """
        sql = "select count(*) as nums from " + cls.table_name + " WHERE to_open_id = %s AND status = 0 limit 1;"
        obj = cls.db_lib.query_for_dict(sql, [open_id])
        return obj['nums']
