# coding:UTF-8

"""
名片社区主程序
"""


from flask import Flask
from app.api import api_app
from app.web_v1 import web_app
from app.admin_v1 import admin_app


app = Flask(__name__)
app.secret_key = 'Ada4ae1a5d33a5e5a8a466b5cebc79aa'
app.register_blueprint(api_app, url_prefix='/api/v1/')
app.register_blueprint(web_app, url_prefix='/web/v1/')
app.register_blueprint(admin_app, url_prefix='/admin/v1/')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
