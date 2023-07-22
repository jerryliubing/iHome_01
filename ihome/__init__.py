# coding:utf-8
from flask import Flask
from config import config_map
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_session import Session
import redis
import logging
from logging.handlers import RotatingFileHandler
import pymysql
pymysql.install_as_MySQLdb()


# 数据库
db = SQLAlchemy()

# redis
redis_store = None

# 配置日志信息
# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  # 调试debug级
# 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
chlr = logging.StreamHandler()  # 输出到控制台的handler
chlr.setFormatter(formatter)
chlr.setLevel('INFO')  # 也可以不设置，不设置就默认用logger的level
logging.getLogger().addHandler(chlr)
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*50, backupCount=10)

# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日记录器
logging.getLogger().addHandler(file_log_handler)





def create_app(config_name):
    # 创建flask应用对象
    app = Flask(__name__)
    config_class = config_map.get(config_name)
    app.config.from_object(config_class)

    db.init_app(app)

    # 创建redis连接对象
    global redis_store
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)

    # 利用flask-session,将session数据保存到redis中
    Session(app)
    # 为flask提供csrf保护
    CSRFProtect(app)

    # 注册蓝图
    from ihome import api_1_0  # 延迟导入，避免循环导包
    app.register_blueprint(api_1_0.api, url_prefix="/api/v1.0")

    return app
