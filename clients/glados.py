import base64

import requests

from libs.base import BaseClient


class Glados(BaseClient):

    def __init__(self):
        super().__init__()

    def run(self, **kwargs):
        try:
            cookie = base64.b64decode(kwargs.get('cookie'))
            self.log(self.checkin(cookie))
        except Exception as e:
            print(e)

    def checkin(self, cookie):
        url = "https://glados.rocks/api/user/checkin"
        referer = 'https://glados.rocks/console/checkin'
        result = requests.post(url, headers={'cookie': cookie, 'referer': referer}).json()
        if result['code'] != 0:
            self.send_tg(f'The cookie has expired\n{cookie}\n{result}')
        return result['message']
