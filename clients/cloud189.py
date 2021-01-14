import base64
import hashlib
import re
import time

import rsa

from libs.base import BaseClient

b64map = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
BI_RM = list("0123456789abcdefghijklmnopqrstuvwxyz")


def int2char(a):
    return BI_RM[a]


def b64_to_hex(a):
    d = ""
    e = 0
    c = 0
    for i in range(len(a)):
        if list(a)[i] != "=":
            v = b64map.index(list(a)[i])
            if 0 == e:
                e = 1
                d += int2char(v >> 2)
                c = 3 & v
            elif 1 == e:
                e = 2
                d += int2char(c << 2 | v >> 4)
                c = 15 & v
            elif 2 == e:
                e = 3
                d += int2char(c)
                d += int2char(v >> 2)
                c = 3 & v
            else:
                e = 0
                d += int2char(c << 2 | v >> 4)
                d += int2char(15 & v)
    if e == 1:
        d += int2char(c << 2)
    return d


def rsa_encode(j_rsa_key, string):
    rsa_key = f"-----BEGIN PUBLIC KEY-----\n{j_rsa_key}\n-----END PUBLIC KEY-----"
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(rsa_key.encode())
    result = b64_to_hex((base64.b64encode(rsa.encrypt(f'{string}'.encode(), pubkey))).decode())
    return result


def calculate_md5_sign(params):
    return hashlib.md5('&'.join(sorted(params.split('&'))).encode('utf-8')).hexdigest()


class Cloud189(BaseClient):

    def __init__(self):
        super().__init__()

    def login(self, username, password):
        url = "https://cloud.189.cn/udb/udb_login.jsp?pageId=1&redirectURL=/main.action"
        r = self.fetch(url)
        captcha_token = re.findall(r"captchaToken' value='(.+?)'", r.text)[0]
        lt = re.findall(r'lt = "(.+?)"', r.text)[0]
        return_url = re.findall(r"returnUrl = '(.+?)'", r.text)[0]
        param_id = re.findall(r'paramId = "(.+?)"', r.text)[0]
        j_rsa_key = re.findall(r'j_rsaKey" value="(\S+)"', r.text, re.M)[0]
        self.headers.update({"lt": lt})

        username = rsa_encode(j_rsa_key, username)
        password = rsa_encode(j_rsa_key, password)
        url = "https://open.e.189.cn/api/logbox/oauth2/loginSubmit.do"
        self.headers['Referer'] = 'https://open.e.189.cn/'
        data = {
            "appKey": "cloud",
            "accountType": '01',
            "userName": f"{{RSA}}{username}",
            "password": f"{{RSA}}{password}",
            "validateCode": "",
            "captchaToken": captcha_token,
            "returnUrl": return_url,
            "mailSuffix": "@189.cn",
            "paramId": param_id
        }
        result = self.fetch(url, data).json()
        self.logger.info(result['msg'])

        if result.get('toUrl'):
            redirect_url = result['toUrl']
            self.fetch(redirect_url)
            return True
        return False

    def run(self, username, password, **kwargs):
        if not self.login(username, password):
            return

        rand = str(round(time.time() * 1000))
        url1 = f'https://api.cloud.189.cn/mkt/userSign.action?rand={rand}&clientType=TELEANDROID&version=8.6.3&model=SM-G930K'
        url2 = f'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN&activityId=ACT_SIGNIN'
        url3 = f'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN_PHOTOS&activityId=ACT_SIGNIN'
        self.headers['Referer'] = 'https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1'
        self.headers['Host'] = 'm.cloud.189.cn'
        self.headers[
            'User-Agent'] = 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clientId/355325117317828 clientModel/SM-G930K imsi/460071114317824 clientChannelId/qq proVersion/1.0.6'
        data = self.fetch(url1).json()
        # net_disk_bonus = data['netdiskBonus']
        self.logger.info(data)

        data = self.fetch(url2).json()
        self.logger.info(data)

        data = self.fetch(url3).json()
        self.logger.info(data)

        # url = f'https://api.telegram.org/bot{self.tg_bot}/sendMessage'
        # self.fetch(url, {'chat_id': self.tg_chat_id, 'text': username, 'parse_mode': 'MarkdownV2'})

