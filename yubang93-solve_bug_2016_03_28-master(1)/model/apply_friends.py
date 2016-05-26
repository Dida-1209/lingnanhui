# coding:UTF-8


"""
好友申请表
@author: yubang
2016.04.02
"""

from model.base_model import BaseModel
from MySQLdb import IntegrityError
from dao import resource_message_dao
import datetime


class ApplyFriendsModel(BaseModel):
    table_name = 'card_apply_friends'
    db = BaseModel.get_db_lib()

    @classmethod
    def apply_friend(cls, source_open_id, target_open_id, remarks):
        """
        申请添加好友
        :param source_open_id: 源用户openid
        :param target_open_id: 目标用户openid
        :param remarks: 备注信息
        :return:
        """
        create_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = "insert into " + cls.table_name + "(source_open_id, target_open_id, create_time, remarks) values(%s, %s, %s, %s);"
        try:
            apply_id = cls.db.insert(sql, [source_open_id, target_open_id, create_time, remarks])
            # 通知对方和自己（小助手）
            resource_message_dao.commit_apply.delay(source_open_id, target_open_id, apply_id)
            return apply_id
        except IntegrityError:
            return 0

    @classmethod
    def handle_apply(cls, apply_id, handle_status, target_open_id):
        """
        标志申请已经处理
        :param apply_id: 申请id
        :param handle_status: 处理状态
        :return:
        """
        sql = "update " + cls.table_name + " set status = %s, handle_sign = null where id = %s AND target_open_id = %s;"
        nums = cls.db.update(sql, [str(handle_status), str(apply_id), target_open_id])
        # 通知对方已经处理
        resource_message_dao.handle_apply.delay(apply_id, handle_status)
        return nums
