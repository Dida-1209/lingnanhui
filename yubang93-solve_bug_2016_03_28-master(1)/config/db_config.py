# coding:UTF-8

"""
数据库配置
2016.02.29
"""

db_name = 'card'
db_host = '127.0.0.1'
db_port = 3306
db_username = 'root'
db_password = ''

redis_host = "127.0.0.1"
redis_port = 6379
redis_db = 4

redis_str = 'redis://%s:%d/%d' % (redis_host, redis_port, redis_db)
