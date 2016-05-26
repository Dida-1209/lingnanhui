# coding:UTF-8


"""
简易redis封装类
@author: yubang
2016.04.02
"""

from config import db_config
import redis

pool = redis.ConnectionPool(host=db_config.redis_host, port=db_config.redis_port, db=db_config.redis_db)
redis_client = redis.Redis(connection_pool=pool)
