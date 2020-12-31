import re

import pyquery

from libs.base import BaseClient


class AppleTuan(BaseClient):

    def __init__(self):
        super(AppleTuan, self).__init__()
        self.base_url = 'https://www.appletuan.com'

    def run(self, **kwargs):
        try:
            cookie = '_qddaz=QD.qwvb5b.ae718f.kfxdha0c; pgv_pvi=9167585280; tencentSig=1203038208; _session_id=jB8%2FXqM721E1wBESsLKSW8QKm4ZTTz%2B2Aevp%2ByKsZbCtXVNgopiDvUfEijR6mXjfBqA2Gf%2BiBYJb1oRIZbB0nkLX%2FgL00uJRlXd6PgqC2Z%2FoRIiYgsxEQM7noBCkJnqnn9j4AOmrO7UHap51yI6jydglDxTeJZh8mTsKefAWcO7Eqh8%2BAZNuS1MjeJUR%2FmqbNt%2ByD5xs6044ID%2FMbWsQb%2FTMBmA5mRRlyhwEhY%2BFgWcgFRfHGLbsLY9Qa6kRuuDiTwZC5FPquf8zwglYX2IBl1MPjAxrxiogWbLjgv1zq3e3BhsRd6sbtrd5IOkCrlSFfDXJecL9eyjKgUUhaY3AyFwg7fELY4cKGApGHRHH2AXUXRJmC07W1W3oPh%2FbtpnBMSjH0elQvWODsiaQLBx1XhXojRA25el%2FuqguL33h5BZ9--AlYEh0%2FTJOgu9tia--gXxGfRxpuqX8VWOoi1lQ8A%3D%3D'
            self.headers['Cookie'] = cookie
            self.headers[
                'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
            html = self.fetch(f'{self.base_url}/checkins').text
            if html.find('users/sign_out') == -1:
                self.logger.warning('not login.')
                return

            doc = pyquery.PyQuery(html)

            credit = doc('.w-3\/12').eq(1).text().replace('0.00', '').strip()
            self.logger.info(f'credit -> {credit}')

            token_name = doc('meta[name=csrf-param]').attr('content')
            token = doc('meta[name=csrf-token]').attr('content')

            self.headers['Referer'] = f'{self.base_url}/checkins'
            self.headers[
                'Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
            params = {'_method': 'post', token_name: token}

            response = self.fetch(f'{self.base_url}/checkins/start', data=params)
            doc = pyquery.PyQuery(response.text)
            credit = doc('.w-3\/12').eq(1).text().replace('0.00', '').strip().split('\n')[0]
            self.logger.info(f'credit -> {credit}')
        except Exception as e:
            self.logger.error(e)
