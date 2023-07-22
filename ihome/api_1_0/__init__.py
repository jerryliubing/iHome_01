# coding:utf-8

from flask import Blueprint

api = Blueprint("api_1_0", __name__)

# 导入蓝图视图
from . import demo

from . import verify_code



