# coding:UTF-8

"""
名片模型
@author: yubang
2016.02.29
"""


from model.base_model import BaseModel
from MySQLdb import IntegrityError, escape_string
from xpinyin import Pinyin
from dao.card_dao import get_update_card_redundancy_labels_dao
from lib.redis_lib import redis_client
from dao import resource_message_dao
from flask import url_for
import datetime


class BusinessCardModel(BaseModel):

    table_name = "card_business_card"
    pinyin_obj = Pinyin()
    db = BaseModel.get_db_lib()

    @classmethod
    def get_table_name(cls):
        return cls.table_name

    @classmethod
    def make_a_card(cls, open_id, name, company, industry, resources_key, avatar, role, invitation_code, province, city, area):
        """
        制作一张名片
        :param open_id: 微信openid
        :param name: 姓名
        :param company: 公司
        :param industry: 行业
        :param resources_key: 资源关键字
        :param role: 职能
        :param invitation_code: 邀请码
        :param province: 省
        :param city: 市
        :param area: 地区
        :return: 返回制作的名片的id，如果名片已经存在则返回0
        """

        create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        name_pinyin = cls.pinyin_obj.get_pinyin(name)
        sql = "insert into " + cls.get_table_name() + "(open_id, name, company, industry, " \
                                                      "resources_key, create_time, avatar, name_pinyin, role, redundancy_labels, invitation_code, province, city, area) values( %s, %s, %s, %s, %s," \
                                                      "%s, %s, %s, %s, %s, %s, %s, %s, %s);"
        db_lib = cls.get_db_lib()

        if cls.has_card(open_id):
            return 0

        try:
            card_id = db_lib.insert(sql, [open_id, name, company, industry, resources_key, create_time, avatar, name_pinyin, role, resources_key, invitation_code, province, city, area])
        except IntegrityError:
            return 0

        # 发送制作名片成功的消息给小助手
        resource_message_dao.send_welcome_message.delay(open_id, url_for('web_app.poster', open_id=open_id, _external=True))

        return card_id

    @classmethod
    def get_name_card(cls, open_id):
        """
        获取个人名片信息，如果没有则返回None
        :param open_id: 微信openid
        :return:
        """
        sql = "select * from " + cls.get_table_name() + " where open_id = %s limit 1;"
        db_lib = cls.get_db_lib()
        obj = db_lib.query_for_dict(sql, [open_id])
        return obj

    @classmethod
    def update_a_card(cls, open_id, name, company, industry, resources_key, avatar, role, invitation_code, province, city, area):
        """
        修改一张名片的信息
        :param open_id: 微信openid
        :param name: 姓名
        :param company: 公司
        :param industry: 行业
        :param resources_key: 资源关键字
        :param role: 职能
        :param invitation_code: 邀请码
        :param province: 省
        :param city: 市
        :param area: 地区
        :return: 返回影响行数
        """
        name_pinyin = cls.pinyin_obj.get_pinyin(name)
        sql = "update " + cls.get_table_name() + " set name = %s, company = %s, industry = %s, " \
                                                 "resources_key = %s, avatar = %s, name_pinyin = %s, role = %s, invitation_code = %s, province = %s, city = %s, area = %s where open_id = %s;"
        db_lib = cls.get_db_lib()
        r = db_lib.update(sql, [name, company, industry, resources_key, avatar, name_pinyin, role, invitation_code, province, city, area, open_id])

        # 异步通知修改冗余标签
        get_update_card_redundancy_labels_dao().delay(open_id)

        # 发送新海报给小助手
        resource_message_dao.send_poster.delay(open_id, url_for('web_app.poster', open_id=open_id, _external=True))

        return r

    @classmethod
    def has_card(cls, open_id):
        """
        判断用户是否已经生成名片
        :param open_id: 微信open_id
        :return:
        """
        # sql = "select count(*) as nums from " + cls.get_table_name() + " where open_id = %s AND status = 0 limit 1;"
        # db_lib = cls.get_db_lib()
        # obj = db_lib.query_for_dict(sql, [open_id])
        # return obj['nums'] != 0

        # 新版处理方法，使用缓存
        return cls.get_user_create_time(open_id) is not None

    @classmethod
    def get_a_page_of_cards(cls, page, count_of_page, search_nickname, order_by_str):
        """
        获取一页名片
        :param page: 页数
        :param count_of_page: 每页记录数
        :param search_nickname: 搜索的昵称
        :param order_by_str: 排序字符串
        :return:
        """
        if page <= 0:
            page = 1
        index = (page - 1) * count_of_page
        limit_str = " limit %d, %d" % (index, count_of_page)

        # 过滤特殊字符
        search_nickname = search_nickname.replace('%', '%%')
        search_nickname = search_nickname.replace("'", "\\'")
        search_nickname = search_nickname.encode("UTF-8")
        sql1 = "select * from " + cls.table_name + " where status = 0 AND name like '%%" + search_nickname + "%%' " + order_by_str + limit_str
        sql2 = "select count(*) as nums from " + cls.table_name + " where status = 0 AND name like '%%" + search_nickname + "%%' limit 1;"

        objs = cls.get_db_lib().query_for_list(sql1, [])
        obj = cls.get_db_lib().query_for_dict(sql2, [])
        objs = map(cls.handle_data_use_in_json, objs)
        return objs, obj['nums']

    @classmethod
    def delete_card(cls, card_id):
        """
        删除一张卡片
        :param card_id: 卡片id
        :return:
        """
        sql = "update " + cls.table_name + " set status = 2 where id = " + str(card_id)
        return cls.get_db_lib().update(sql, [])

    @classmethod
    def recommend_card(cls, card_id, status):
        """
        处理小编推荐
        :param card_id: 名片id
        :param status: 推荐状态
        :return:
        """
        sql = "update " + cls.table_name + " set is_recommend = %d where id = %d"
        return cls.get_db_lib().update(sql % (status, card_id), [])

    @classmethod
    def get_recommend_cards(cls, own_open_id, page, count_of_page):
        """
        获取小编推荐名片
        :param own_open_id: 自己的open_id
        :param page: 页数
        :param count_of_page: 每页记录数
        :return:数据列表（list），总记录数（int），页数（int）
        """
        # 检测类型
        if type(page) != int or type(count_of_page) != int:
            raise Exception(u'args type error!')

        # 处理异常数据
        if page <= 0:
            page = 1
        # 计算偏移量
        index = (page - 1) * count_of_page

        sql = """
            select * from %s where status = 0 AND is_recommend = 1
            AND open_id != '%s'
            order by update_time desc
            limit %d, %d
        """ % (cls.table_name, escape_string(own_open_id), index, count_of_page)
        objs = cls.get_db_lib().query_for_list(sql)
        objs = map(cls.handle_data_use_in_json, objs)

        sql = """
            select count(*) as nums from %s where status = 0 AND is_recommend = 1
            AND open_id != '%s'
            order by update_time desc
            limit 1
        """ % (cls.table_name, escape_string(own_open_id))
        obj = cls.get_db_lib().query_for_dict(sql)

        max_page = obj['nums'] / count_of_page
        if obj['nums'] % count_of_page:
            max_page += 1

        return objs, obj['nums'], max_page

    @classmethod
    def get_own_recommend_cards(cls, open_id, page, count_of_page):
        """
        获取个人推荐的名片（同行业）
        :param open_id: 微信openid
        :param page: 页数
        :param count_of_page: 每页记录数
        :return: 数据列表（list），总记录数（int），页数（int）
        """
        # 检测类型
        if type(page) != int or type(count_of_page) != int:
            raise Exception(u'args type error!')

        # 处理异常数据
        if page <= 0:
            page = 1
        # 计算偏移量
        index = (page - 1) * count_of_page

        # 拉取个人信息
        own_card = cls.get_name_card(open_id)
        own_card['industry'] = escape_string(own_card['industry'].encode("UTF-8"))

        sql = """
            select * from %s where status = 0 AND industry = '%s' AND open_id != '%s'
            order by update_time desc limit %d,%d
        """ % (cls.table_name, own_card['industry'].decode("UTF-8"), open_id, index, count_of_page)

        sql2 = """
            select count(*) as nums from %s where status = 0 AND industry = '%s' AND open_id != '%s'
            order by update_time desc limit 1
        """ % (cls.table_name, own_card['industry'].decode("UTF-8"), open_id)

        objs = cls.get_db_lib().query_for_list(sql)
        objs = map(cls.handle_data_use_in_json, objs)

        obj = cls.get_db_lib().query_for_dict(sql2)

        max_page = obj['nums'] / count_of_page
        if obj['nums'] % count_of_page:
            max_page += 1

        return objs, obj['nums'], max_page

    @classmethod
    def search_cards(cls, own_open_id, industry, role, search_key, page, count_of_page):
        """
        搜索标签
        :param own_open_id: 自己的openid
        :param industry: 搜索的行业
        :param role: 搜索的职能
        :param page: 页数
        :param count_of_page: 每页记录数
        :return: 数据列表（list），总记录数（int），页数（int）
        """

        if type(page) != int or type(count_of_page) != int:
            raise Exception('argv type error!')

        # 处理异常数据
        if page <= 0:
            page = 1
        # 计算偏移量
        index = (page - 1) * count_of_page

        sql = """
            select * from %s
            where status = 0 AND open_id != '%s' AND (redundancy_labels like '%%%s%%'
            OR name like '%%%s%%' OR company like '%%%s%%')
            AND industry like '%%%s%%' AND role like '%%%s%%'
            order by update_time desc
            limit %d, %d;
        """ % (cls.table_name, escape_string(own_open_id), escape_string(search_key), escape_string(search_key), escape_string(search_key), escape_string(industry), escape_string(role), index, count_of_page)

        objs = cls.get_db_lib().query_for_list(sql)
        objs = map(cls.handle_data_use_in_json, objs)

        sql = """
            select count(*) as nums from %s
            where status = 0 AND open_id != '%s' AND (redundancy_labels like '%%%s%%'
            OR name like '%%%s%%' OR company like '%%%s%%')
            AND industry like '%%%s%%' AND role like '%%%s%%'
            order by update_time desc
            limit 1;
        """ % (cls.table_name, escape_string(own_open_id), escape_string(search_key), escape_string(search_key), escape_string(search_key), escape_string(industry), escape_string(role),)
        obj = cls.get_db_lib().query_for_dict(sql)

        max_page = obj['nums'] / count_of_page
        if obj['nums'] % count_of_page:
            max_page += 1

        return objs, obj['nums'], max_page

    @classmethod
    def get_tags_from_own_friends(cls, open_id):
        """
        获取一个用户的朋友的所有标签
        :param open_id:
        :return:
        """
        sql = """
            select card_business_card.resources_key from card_friends
            left join card_business_card on  card_business_card.open_id = card_friends.target_open_id
            WHERE card_friends.source_open_id = %s
        """
        objs = cls.db.query_for_list(sql, [open_id])
        objs = map(lambda obj: obj['resources_key'], objs)

        return objs

    @classmethod
    def get_tags_use_list(cls, datas):
        """
        获取不重复的标签数据
        :param datas: 列表 ['标签字符串', '标签字符串', '标签字符串'...]
        :return: set
        """
        tags = set()

        for obj in datas:
            ds = obj.split('#')
            for d in ds:
                tags.add(d)

        return tags

    @classmethod
    def get_own_tags_in_own_and_friend(cls, open_id):
        """
        获取一层人脉的所有标签
        :param open_id: 用户openid
        :return: []
        """
        friend_tags = cls.get_tags_from_own_friends(open_id)
        own = cls.get_name_card(open_id)

        r = [own['resources_key']]
        r.extend(friend_tags)
        tags = cls.get_tags_use_list(r)
        return tags

    @classmethod
    def update_user_redundancy_labels(cls, open_id):
        """
        更新名片冗余的标签信息
        :param open_id: 用户openid
        :return:
        """
        tags = cls.get_own_tags_in_own_and_friend(open_id)
        tag_str = '#'.join(tags)

        sql = "update " + cls.table_name + " set redundancy_labels = %s where open_id = %s;"
        return cls.db.update(sql, [tag_str, open_id])

    @classmethod
    def check_invitation_code(cls, invitation_code):
        """
        检测邀请码是否正确
        :param invitation_code: 邀请码
        :return:
        """
        return invitation_code == '1888'

    @classmethod
    def get_user_create_time(cls, open_id):
        """
        获取用户创建时间
        :param open_id: 用户openid
        :return: 如果用户没有创建则为None
        """
        cache_key = "data_user_create_time_" + open_id
        cache_data = redis_client.get(cache_key)

        if cache_data:
            return cache_data

        # 缓存没有数据，尝试从数据库查
        card = cls.get_name_card(open_id)
        if not card:
            return None

        cache_data = card['create_time'].strftime("%Y-%m-%d %H:%M:%S")
        redis_client.set(cache_key, cache_data)
        return cache_data
