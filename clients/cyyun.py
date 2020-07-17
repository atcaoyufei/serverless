import re
import time

import pyquery

from libs.base import BaseClient


class CyYun(BaseClient):

    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.cyyun.net'

    def _handler(self, username, password, **kwargs):
        response = self.login(username, password)
        result = response.json()
        if result['ret'] == 0:
            raise Exception(result)

        if self.info(username):
            self.logger.info(self.sign())

    def info(self, username):
        html = self.fetch(f'{self.base_url}/user', allow_redirects=False).text
        doc = pyquery.PyQuery(html)
        container = doc('.container .row').eq(0)
        expire_info = container('.text-dark-50').eq(1).text().replace(' : ', ': ').strip()

        if expire_info.find('企图白嫖') != -1 or time.strftime('%Y-%m-%d') == re.search(r'\d{4}-\d+-\d+',
                                                                                    expire_info).group():
            self.buy()
            return self.info(username)

        # expire_date = container('.font-size-h4 .counter').text()
        traffic = container('.font-size-h4').eq(1).text()
        self.logger.info(username, expire_info, traffic)
        return html.find('已签到') == -1

    def sign(self):
        return self.fetch(f'{self.base_url}/user/checkin', method='POST').json()['msg']

    def buy(self):
        return self.fetch(f'{self.base_url}/user/buy',
                          {'shop': 3, 'autorenew': '0', 'disableothers': '1', 'coupon': ''}).json()

    def login(self, username, password):
        data = {'remember_me': 'on', 'email': username, 'passwd': password, 'code': ''}
        return self.fetch(f'{self.base_url}/auth/login', data)
