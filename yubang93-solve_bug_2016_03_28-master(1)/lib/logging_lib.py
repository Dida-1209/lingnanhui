# coding:UTF-8


"""
记录日志模块
@author: yubang
2016.04.09
"""


import logging

LOG_FILE = 'log/app'
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILE, 'D', 1, 0)# 实例化handler

fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(funcName)s - %(message)s'
formatter = logging.Formatter(fmt)   # 实例化formatter
handler.setFormatter(formatter)      # 为handler添加formatter
handler.suffix = "%Y%m%d-%H%M.log"
log = logging.getLogger('own_logger')
log.setLevel(logging.INFO)
log.addHandler(handler)



