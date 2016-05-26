# coding:UTF-8


"""
群报名记录表
@author: yubang
2016.03.30
"""


from model.base_model import BaseModel
from MySQLdb import escape_string


class GroupRecordModel(BaseModel):
    table_name = 'card_group_record'
    db = BaseModel.get_db_lib()

    @classmethod
    def has_join_group(cls, open_id, group_token):
        """
        是否已进加入该群
        :param open_id: 用户openid
        :param group_token: 群凭证
        :return:
        """
        sql = "select count(*) as nums from " + cls.table_name + " where open_id = %s AND group_token = %s limit 1;"
        obj = cls.db.query_for_dict(sql, [open_id, group_token])
        return obj['nums'] != 0

    @classmethod
    def join_group(cls, open_id, group_token):
        """
        加入群
        :param open_id: 用户openid
        :param group_token: 群凭证
        :return:
        """
        sql = "insert into " + cls.table_name + "(open_id, group_token, create_time) values(%s, %s, now());"
        return cls.db.insert(sql, [open_id, group_token])

    @classmethod
    def get_all_card_in_a_group(cls, group_token, page, count_of_page, search_key, industry, role):
        """
        获取一个群的所有名片
        :param group_token: 群凭证
        :return:
        """

        if type(page) != int or type(count_of_page) != int:
            raise Exception("args type error!")

        if page <= 0:
            page = 1
        index = (page - 1) * count_of_page
        limit_str = " limit %d, %d" % (index, count_of_page)

        search_str = """
            AND (card_business_card.name like '%%%s%%' OR card_business_card.company like '%%%s%%'
            OR card_business_card.redundancy_labels like '%%%s%%') AND card_business_card.industry like '%%%s%%'
            AND card_business_card.role like '%%%s%%'
        """ % (escape_string(search_key), escape_string(search_key), escape_string(search_key), escape_string(industry),
               escape_string(role))
        search_str = search_str.replace('%', '%%')
        sql = """
            select card_business_card.* from card_group_record
            left join card_business_card on card_group_record.open_id = card_business_card.open_id
            WHERE card_group_record.group_token = %s AND card_business_card.status = 0
        """ + search_str + """
            order by card_business_card.name_pinyin ASC
        """ + limit_str
        objs = cls.db.query_for_list(sql, [group_token])
        objs = map(cls.handle_data_use_in_json, objs)

        sql = """
            select count(*) as nums from card_group_record
            left join card_business_card on card_group_record.open_id = card_business_card.open_id
        """ + search_str + """
            WHERE card_group_record.group_token = %s AND card_business_card.status = 0
            limit 1
        """
        obj = cls.db.query_for_dict(sql, [group_token])

        max_page = obj['nums'] / count_of_page
        if obj['nums'] % count_of_page:
            max_page += 1

        return {"objs": objs, "total_nums": obj['nums'], "total_page": max_page}

