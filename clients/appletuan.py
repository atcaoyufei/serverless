import re

import pyquery

from libs.base import BaseClient


class AppleTuan(BaseClient):

    def __init__(self):
        super(AppleTuan, self).__init__()
        self.base_url = 'https://www.appletuan.com'

    def run(self, **kwargs):
        try:
            cookie = '_qddaz=QD.qwvb5b.ae718f.kfxdha0c; pgv_pvi=9167585280; tencentSig=1203038208; _session_id=tj6spRfBtZp7Mmb%2BJGuIttMcTUKnfzHJFaXRJsLaWqI0B8G7dy5DiMQkFBz6nPp%2BKZZiwe9VjdYx05dcKS4NSTNMRhdgTXR0Th79LVdRsgNyzRuqKhces3kNJMgFvzerf5f0DlOvpTZ%2FYQ%2Feo9SEq4YKl6moGYZTiHBSyintS7LEk7t7JEOyVeaTIraNJQHJleVJJBK%2B15RtNfNiujjZZexZGd83mmDucKyviYWsnUAS25G2Mv3ARcCBKnYqc%2Bsj%2BznP6nH3iTVs5Xq4xrH0at7HAbMH3aCgfzAL0w4BDNmLK44WUNjZ46DJQaEgey7STk0nGvRHJp2cqMUbqleTIRhTcWXYZX%2Fz1IuI4xRTAY%2Bewqo7xPPJx5ewLm9jxkK8idok0uoi5FL36Y6RjZp2VvSfiGO6TKTOw3J59Q09PgKF3GolHd57DLkrBKaC--5%2BmHNRAkerp0xZSj--MiNceJRc0di9ovrSdMT2NA%3D%3D'
            self.headers['Cookie'] = cookie
            self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
            html = self.fetch(f'{self.base_url}/checkins').text
            if html.find('users/sign_out') == -1:
                self.logger.warning('not login.')
                return

            # doc = pyquery.PyQuery(html)
            # credit = doc('.w-3\/12').eq(1).text().replace('0.00', '').strip()
            # self.logger.info(f'credit -> {credit}')

            self.headers['Referer'] = f'{self.base_url}/checkins'
            self.headers['Origin'] = self.base_url
            self.headers['Host'] = 'www.appletuan.com'
            token = re.search(r'<meta name="csrf-token" content="([^\"]+)" />', html).group(1)
            params = {'_method': 'post', 'authenticity_token': token}

            response = self.fetch(f'https://www.appletuan.com/checkins/start', params)
            doc = pyquery.PyQuery(response.text)
            credit = doc('.w-3\/12').eq(1).text().replace('0.00', '').strip()
            self.logger.info(f'credit -> {credit}')
        except Exception as e:
            self.logger.error(e)
