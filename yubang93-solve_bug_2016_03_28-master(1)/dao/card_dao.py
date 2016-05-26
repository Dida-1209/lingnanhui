# coding:UTF-8


"""
名片接口
@author: yubang
2016.03.31
"""

__update_card_redundancy_labels_dao = None


def set_update_card_redundancy_labels_dao(celery_obj, friendModel, businessCardModel):
    global __update_card_redundancy_labels_dao

    @celery_obj.task
    def update_card_redundancy_labels(open_id, open_id2=None):
        """
        处理名片数据改动后，数据一致性问题
        :param open_id:
        :return:
        """
        friend_open_ids = set()
        friends1 = friendModel.get_all_friends(open_id)
        for obj in friends1:
            friend_open_ids.add(obj['open_id'])
        friend_open_ids.add(open_id)

        if open_id2:
            friends2 = friendModel.get_all_friends(open_id2)
            for obj in friends2:
                friend_open_ids.add(obj['open_id'])

            friend_open_ids.add(open_id2)

        for obj in friend_open_ids:
            businessCardModel.update_user_redundancy_labels(obj)

    __update_card_redundancy_labels_dao = update_card_redundancy_labels


def get_update_card_redundancy_labels_dao():
    return __update_card_redundancy_labels_dao
