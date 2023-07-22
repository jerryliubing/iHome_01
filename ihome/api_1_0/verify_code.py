# coding:utf-8
from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store
from ihome.constants import IMAGE_CODE_REDIS_EXPIRES
from flask import jsonify, make_response, current_app
from ihome.utils.response_code import RET

@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """
    获取图片验证码
    :param image_code_id: str 图片验证码id
    :return: 正常：图片验证码   异常：json
    """
    # 生成图片验证码
    name, text, image_data = captcha.generate_captcha()
    # 在redis中保存生成的图片验证码
    try:
        redis_store.setex("image_code_%s" % image_code_id, IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存图片验证码失败")

    resp = make_response(image_data)
    resp.headers["Content-Type"] = "image/jpg"

    return resp








