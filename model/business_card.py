# coding:UTF-8

"""
名片模型
@author: yubang
2016.02.29
"""


from model.base_model import BaseModel
from MySQLdb import IntegrityError, escape_string
from xpinyin import Pinyin


class BusinessCardModel(BaseModel):

    table_name = "card_business_card"
    pinyin_obj = Pinyin()

    @classmethod
    def get_table_name(cls):
        return cls.table_name

    @classmethod
    def make_a_card(cls, open_id, name, company, industry, resources, resources_label, resources_key, avatar):
        """
        制作一张名片
        :param open_id: 微信openid
        :param name: 姓名
        :param company: 公司
        :param industry: 行业
        :param resources: 能提供的资源
        :param resources_label: 资源标签
        :param resources_key: 资源关键字
        :return: 返回制作的名片的id，如果名片已经存在则返回0
        """
        name_pinyin = cls.pinyin_obj.get_pinyin(name)
        sql = "insert into " + cls.get_table_name() + "(open_id, name, company, industry, resources, resources_label, " \
                                                      "resources_key, create_time, avatar, name_pinyin) values(%s, %s, %s, %s, %s, %s, %s," \
                                                      "now(), %s, %s);"
        db_lib = cls.get_db_lib()

        if cls.has_card(open_id):
            return 0

        try:
            card_id = db_lib.insert(sql, [open_id, name, company, industry, resources, resources_label, resources_key, avatar, name_pinyin])
        except IntegrityError:
            return 0

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
    def update_a_card(cls, open_id, name, company, industry, resources, resources_label, resources_key, avatar):
        """
        修改一张名片的信息
        :param open_id: 微信openid
        :param name: 姓名
        :param company: 公司
        :param industry: 行业
        :param resources: 能提供的资源
        :param resources_label: 资源标签
        :param resources_key: 资源关键字
        :return: 返回影响行数
        """
        name_pinyin = cls.pinyin_obj.get_pinyin(name)
        sql = "update " + cls.get_table_name() + " set name = %s, company = %s, industry = %s, resources = %s, " \
                                                 "resources_label = %s, resources_key = %s, avatar = %s, name_pinyin = %s where open_id = %s;"
        db_lib = cls.get_db_lib()
        r = db_lib.update(sql, [name, company, industry, resources, resources_label, resources_key, avatar, name_pinyin, open_id])
        return r

    @classmethod
    def has_card(cls, open_id):
        """
        判断用户是否已经生成名片
        :param open_id: 微信open_id
        :return:
        """
        sql = "select count(*) as nums from " + cls.get_table_name() + " where open_id = %s AND status = 0 limit 1;"
        db_lib = cls.get_db_lib()
        obj = db_lib.query_for_dict(sql, [open_id])
        return obj['nums'] != 0

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
        own_card['industry'] = escape_string(own_card['industry'])

        sql = """
            select * from %s where status = 0 AND industry = '%s' AND open_id != '%s'
            order by update_time desc limit %d,%d
        """ % (cls.table_name, own_card['industry'], open_id, index, count_of_page)

        sql2 = """
            select count(*) as nums from %s where status = 0 AND industry = '%s' AND open_id != '%s'
            order by update_time desc limit 1
        """ % (cls.table_name, own_card['industry'], open_id)

        objs = cls.get_db_lib().query_for_list(sql)
        objs = map(cls.handle_data_use_in_json, objs)

        obj = cls.get_db_lib().query_for_dict(sql2)

        max_page = obj['nums'] / count_of_page
        if obj['nums'] % count_of_page:
            max_page += 1

        return objs, obj['nums'], max_page

    @classmethod
    def search_cards(cls, own_open_id, name, company, resources_label, resources_key, page, count_of_page):
        """
        搜索标签
        :param own_open_id: 自己的openid
        :param name: 搜索的名字
        :param company: 搜索的公司名
        :param resources_label: 搜索的资源标签
        :param resources_key: 搜索的自定义标签
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
            where status = 0 AND open_id != '%s' AND name like '%%%s%%'
            AND company like '%%%s%%' AND resources_label like '%%%s%%'
            AND resources_key like '%%%s%%'
            order by update_time desc
            limit %d, %d;
        """ % (cls.table_name, escape_string(own_open_id), escape_string(name), escape_string(company), escape_string(resources_label), escape_string(resources_key), index, count_of_page)
        objs = cls.get_db_lib().query_for_list(sql)
        objs = map(cls.handle_data_use_in_json, objs)

        sql = """
            select count(*) as nums from %s
            where status = 0 AND open_id != '%s' AND name like '%%%s%%'
            AND company like '%%%s%%' AND resources_label like '%%%s%%'
            AND resources_key like '%%%s%%'
            order by update_time desc
            limit 1;
        """ % (cls.table_name, escape_string(own_open_id), escape_string(name), escape_string(company), escape_string(resources_label), escape_string(resources_key))
        obj = cls.get_db_lib().query_for_dict(sql)

        max_page = obj['nums'] / count_of_page
        if obj['nums'] % count_of_page:
            max_page += 1

        return objs, obj['nums'], max_page
