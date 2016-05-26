# coding:UTF-8


"""
数据库模型基类
"""

from lib import db_lib


class BaseModel(object):

    table_name = None

    @classmethod
    def get_db_lib(cls):
        return db_lib

    @classmethod
    def handle_data_use_in_json(cls, obj):
        if 'create_time' in obj:
            obj['create_time'] = obj['create_time'].strftime("%Y-%m-%d %H:%M:%S")
        if 'update_time' in obj:
            obj['update_time'] = obj['update_time'].strftime("%Y-%m-%d %H:%M:%S")
        if 'uptime_time' in obj:
            obj['uptime_time'] = obj['uptime_time'].strftime("%Y-%m-%d %H:%M:%S")
        return obj

    @classmethod
    def get_one_page_of_table(cls, own_table_names, where_str, page, count_of_page, order_by=None):
        """
        获取一页数据
        :param own_table_names: 表的名字（from XXX,[XXX],[xxx]）
        :param where_str: where 字符串（where XXX）
        :param page: 第几页（int）
        :param count_of_page: 每页多少记录数（int）
        :return: {"total_nums": 总记录数, "total_page": 总页数, "objs": [获取到的数据]}
        """

        if type(page) != int or type(count_of_page) != int:
            raise Exception("args type error!")

        if page <= 0:
            page = 1
        index = (page - 1) * count_of_page
        limit_str = " limit %d, %d" % (index, count_of_page)

        if order_by:
            order_by = " order by " + order_by
        else:
            order_by = ''

        sql = "select * from " + own_table_names + " where " + where_str + order_by + (" limit %d,%d;" % (index, count_of_page))
        objs = cls.get_db_lib().query_for_list(sql)
        objs = map(cls.handle_data_use_in_json, objs)

        sql = "select count(*) as nums from " + own_table_names + " where " + where_str + " limit 1;"
        obj = cls.get_db_lib().query_for_dict(sql)

        max_page = obj['nums'] / count_of_page
        if obj['nums'] % count_of_page:
            max_page += 1

        return {"objs": objs, "total_nums": obj['nums'], "total_page": max_page}

    @classmethod
    def find_by_id(cls, table_id):
        """
        根据主键获取一条数据
        :param table_id: 主键id
        :return:
        """

        if type(table_id) != int:
            raise Exception("args type error!")

        sql = "select * from %s where id = %d limit 1;" % (cls.table_name, table_id)
        return cls.get_db_lib().query_for_dict(sql)
