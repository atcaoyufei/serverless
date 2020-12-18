import base64

import requests

from libs.base import BaseClient


class Glados(BaseClient):

    def __init__(self):
        super().__init__()

    def run(self, **kwargs):
        try:
            # cookie = base64.b64decode(kwargs.get('cookie')).decode('utf-8')
            cookie = 'koa:sess=eyJ1c2VySWQiOjQyMzU2LCJfZXhwaXJlIjoxNjI3MzY2NDUzMzU3LCJfbWF4QWdlIjoyNTkyMDAwMDAwMH0=; koa:sess.sig=1cAg4N7AurgOGQ6DObSAi2qmwJ4'
            self.logger.info(self.checkin(cookie))
        except Exception as e:
            print(e)

    def checkin(self, cookie):
        url = "https://glados.rocks/api/user/checkin"
        referer = 'https://glados.rocks/console/checkin'
        result = requests.post(url, {'token': 'glados_network'}, headers={'cookie': cookie, 'referer': referer}).json()
        if result['code'] != 0:
            self.logger.error(result)
        return result['message']
