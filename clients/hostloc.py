import re

import requests
from requests.cookies import cookiejar_from_dict

from libs.discuz import Discuz


class Hostloc(Discuz):

    def __init__(self):
        super(Hostloc, self).__init__()
        self.base_url = 'https://www.hostloc.com'

    def _handler(self, username, password, **kwargs):
        data = self.login(username, password)
        self.log(data['message'])
        if not self.is_ok(data):
            return

        self.log(self.user_info()['message'])
        self.views()
        self.log(self.user_info()['message'])

    def login(self, username, password, max_retry=4):
        login_url = f"{self.base_url}/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1"
        login_data = {
            "username": username,
            "password": password,
        }
        response = self.fetch(login_url, data=login_data)
        html = response.text
        _aes = re.findall(r'toNumbers\("([^"]+)"', html, flags=re.S)
        if _aes:
            aes_url = f'https://us-south.functions.cloud.ibm.com/api/v1/web/atcaoyufei_namespace-south/default/aes/?a={_aes[0]}&b={_aes[1]}&c={_aes[2]}'
            # aes_url = f'https://donjs.herokuapp.com/aes/{_aes[0]}/{_aes[1]}/{_aes[2]}'
            aes_cookie = requests.get(aes_url).text
            # self.headers['Cookie'] = f'L7DFW={aes_cookie}'
            self.http.cookies = cookiejar_from_dict({'L7DFW': aes_cookie})
            self.fetch(login_url, data=login_data)
            response = self.fetch(f'{self.base_url}/home.php?mod=spacecp&ac=credit')
            html = response.text

        if html.find(username) == -1:
            return self.error(f'login fail.')
        return self.success(f'login success', data={'cookie': response.cookies})
