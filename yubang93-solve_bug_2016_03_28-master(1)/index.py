# coding:UTF-8

"""
名片社区主程序
"""

# 主入口
from flask import Flask, session
app = Flask(__name__)

# 配置异步处理
from config.db_config import redis_str
from dao.clery_obj_make_dao_in_index import make_celery
app.config['CELERY_BROKER_URL'] = redis_str
app.config['CELERY_RESULT_BACKEND'] = redis_str
app.secret_key = 'Ada4ae1a5d33a5e5a8a466b5cebc79aa'

# 注册异步处理类
celery_obj = make_celery(app)

# 加载全局变量
from dao import other_dao
other_dao.celery_obj_dao = celery_obj
other_dao.flask_app = app

# 挂载蓝图
from app.api import api_app
from app.web_v1 import web_app
from app.admin_v1 import admin_app
app.register_blueprint(api_app, url_prefix='/api/v1/')
app.register_blueprint(web_app, url_prefix='/web/v1/')
app.register_blueprint(admin_app, url_prefix='/admin/v1/')

# 特殊处理一个异步
from model.friend_model import FriendModel
from model.business_card import BusinessCardModel
from model.apply_friends import ApplyFriendsModel
from dao import card_dao
card_dao.set_update_card_redundancy_labels_dao(celery_obj, FriendModel, BusinessCardModel)

# 注册模型
from dao.all_model import model_manager
from model.resource_helper_message_model import ResourceHelperMessageModel
model_manager['BusinessCardModel'] = BusinessCardModel
model_manager['ApplyFriendsModel'] = ApplyFriendsModel
model_manager['ResourceHelperMessageModel'] = ResourceHelperMessageModel


@app.route('/debug')
def debug():
    session.pop('open_id', None)
    session.pop('user_data', None)
    session.pop('group_token', None)
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True, threaded=True)
