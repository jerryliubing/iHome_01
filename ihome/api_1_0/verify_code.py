# coding:utf-8
from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store
from ihome import constants
from flask import jsonify, make_response, current_app, request
from ihome.utils.response_code import RET
from ihome.models import User
from ihome.libs.yuntongxun.sms import CCP
import random


@api.route("/image_codes/<image_code_id>")
def get_image_code(image_code_id):
    """
    获取图片验证码
    :param image_code_id: str 图片验证码id
    :return: 正常：图片验证码   异常：json
    """
    # 生成图片验证码
    name, text, image_data = captcha.generate_captcha()
    print "-=-=-=-=-=-"
    print "image_code: %s" % text
    print "-=-=-=-=-=-"
    # 在redis中保存生成的图片验证码
    try:
        redis_store.setex("image_code_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存图片验证码失败")

    resp = make_response(image_data)
    resp.headers["Content-Type"] = "image/jpg"

    return resp


# GET /api/v1.0/sms_codes/18622344111?image_code=xxx&image_code_id=xxx
@api.route("/sms_codes/<re(r'1[34578]\d{9}'):mobile>")
def send_sms_code(mobile):
    """
    获取短信验证码
    :return: json
    """
    # 获取参数
    image_code = request.args.get("image_code")
    image_code_id = request.args.get("image_code_id")

    # 校验参数
    if not all([image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 业务逻辑
    # 从redis中获取真实的image_code
    try:
        real_image_code = redis_store.get("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="redis数据库异常")
    # 判断image_code是否过期
    if real_image_code is None:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码失效")

    # 删除redis中的图片验证码数据，防止用户对同一个验证码校验多次
    try:
        redis_store.delete("image_code_%s" % image_code_id)
    except Exception as e:
        current_app.logger.error(e)

    # 与用户比较是否一致
    if real_image_code.lower() != image_code.lower():
        return jsonify(errno=RET.DATAERR, errmsg="用户图片验证码填写错误")

    # 判断这个手机号的操作，在60秒内有没有之前的记录，如果有，则任务用户操作频繁，不接受处理
    try:
        send_flag = redis_store.get("send_sms_code_%s" % mobile)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if send_flag is not None:
            # 表示60秒内有记录
            return jsonify(errno=RET.REQERR, errmsg="用户操作频繁，请60秒后重试")

    # 判断该手机号是否注册
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
    else:
        # 手机号已经注册
        if user is not None:
            return jsonify(errno=RET.DATAEXIST, errmsg="手机号已经注册")
    # 手机号未注册
    sms_code = "%04d" % random.randint(0, 9999)
    print "-=-=-=-=-=-"
    print "sms_code: %s" % sms_code
    print "-=-=-=-=-=-"
    # 生成短信验证码，并存储在redis中
    try:
        redis_store.setex("sms_code_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        redis_store.setex("send_sms_code_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="redis保存短信验证码异常")

    # 发送短信验证码
    # try:
    #     ccp = CCP()
    #     result = ccp.send_template_sms(mobile, [sms_code, int(constants.SMS_CODE_REDIS_EXPIRES/60)], 1)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.THIRDERR, errmsg="发送异常")
    result = 0

    # 返回值
    if result == 0:
        # 发送成功
        return jsonify(errno=RET.OK, errmsg="发送成功")
    else:
        # 发送失败
        return jsonify(errno=RET.THIRDERR, errmsg="发送失败")






