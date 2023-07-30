# coding:utf-8

from CCPRestSDK import REST
import ssl
"""
python升级到2.7.9之后引入了一个新特性，当打开一个https连接时，会验证一次SSL证书。而当目标网站使用的是自签名的证书时，就会出现异常。
"""
ssl._create_default_https_context=ssl._create_unverified_context


# 主帐号
accountSid = '8a216da864f9f15b01650a6f33bb0bc8'

# 主帐号Token
accountToken = 'b3f4b22a07e24489a17117b2dcce2c94'

# 应用Id
appId = '8a216da864f9f15b01650a6f34190bcf'

# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

# 请求端口
serverPort = '8883'

# REST版本号
softVersion = '2013-12-26'

  # 发送模板短信
  # @param to 手机号码
  # @param datas 内容数据 格式为列表 例如：['12','34']，如不需替换请填 ''
  # @param $tempId 模板Id


class CCP(object):
    """
    封装的发送短信类
    """
    # 单例模式
    # 保存对象的类属性
    instance = None

    def __new__(cls):
        if cls.instance is None:
            # 没有对象实例化
            obj = super(CCP, cls).__new__(cls)
            # 初始化REST SDK
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)

            cls.instance = obj

        return cls.instance

    def send_template_sms(self, to, datas, temp_id):
        """
        发送短信
        :param to: str，手机号
        :param datas: 列表，[内容，过期时间]
        :param temp_id: str, 模板id：测试模式默认0
        :return: int； 0：发送成功 1：发送失败
        """
        result = self.rest.sendTemplateSMS(to, datas, temp_id)
        status_code = result.get("statusCode")
        print(status_code)
        if status_code == "000000":
            # 表示发送短信成功
            return 0
        else:
            # 发送失败
            return -1


if __name__ == '__main__':
    ccp = CCP()
    ret = ccp.send_template_sms("18622344618", [1234, 5], 1)
    print(ret)

    
   
