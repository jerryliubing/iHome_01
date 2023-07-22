# coding:utf-8
from flask import Blueprint, current_app, make_response
from flask_wtf import csrf


html = Blueprint("web_html", __name__)


@html.route("/<re(r'.*'):html_file_name>")
def get_html(html_file_name):
    """
    提供HTML文件
    :param html_file_name: str，正则转换器获取到的url中HTML文件名
    :return:response对象
    """
    # 127.0.0.1:5000/
    # 127.0.0.1:5000/(register.html)
    # 127.0.0.1:5000/favicon.ico

    # html_file_name为""，表示路径为/，请求的是主页
    if not html_file_name:
        html_file_name = "index.html"
    if html_file_name != "favicon.ico":
        html_file_name = "html/" + html_file_name

    # 创建csrf_token值
    csrf_token = csrf.generate_csrf()
    # 将csrf_token设置到cookie中
    resp = make_response(current_app.send_static_file(html_file_name))
    resp.set_cookie("csrf_token", csrf_token)

    return resp

