import logging
import os
import time
from datetime import datetime, timedelta, timezone

import requests
from requests.cookies import cookiejar_from_dict
from telegram import Bot


class BaseClient:

    def __init__(self):
        self.base_url = None
        self.http = requests.session()
        self.charset = 'utf-8'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
        }
        self.logger = logging.getLogger(self.__class__.__name__)
        self.tg_bot = os.environ.get('tg_bot')
        self.tg_chat_id = os.environ.get('tg_chat_id')

        self.utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8)))
        self.now_time = self.utc_dt.strftime('%Y-%m-%d %H:%M:%S')

    def run(self, **kwargs):
        username_list = kwargs.get('username').split(',')
        password_list = kwargs.get('password').split(',')

        if len(password_list) > 1 and len(password_list) != len(username_list):
            raise Exception('The number of accounts and passwords is different.')

        del kwargs['username']
        del kwargs['password']
        for i, username in enumerate(username_list):
            password = password_list[0] if len(password_list) == 1 else password_list[i]
            try:
                self.http.cookies = cookiejar_from_dict({})
                self._handler(username=username, password=password, **kwargs)
            except Exception as e:
                print(e)

        # self.client.disconnect()

    def _handler(self, username, password, **kwargs):
        pass

    def fetch(self, url, data=None, method='GET', **kwargs):
        kwargs.setdefault('timeout', 20)
        kwargs.setdefault('headers', self.headers)

        if data:
            method = 'POST'

        response = self.http.request(method, url, data=data, **kwargs)
        if response.ok:
            response.encoding = self.charset
            return response
        raise Exception(response.status_code, url, response.text)

    def send_tg(self, message, **kwargs):
        if self.tg_bot and self.tg_chat_id:
            bot = Bot(self.tg_bot)
            bot.send_message(chat_id=self.tg_chat_id, text=message, **kwargs)

    @staticmethod
    def log(*args):
        utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
        message = utc_dt.astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
        for arg in args:
            message = f'{message} {str(arg)}'
        print(message)

    @staticmethod
    def success(message, data=None):
        return {'code': 0, 'message': message, 'data': data}

    @staticmethod
    def error(message, data=None, code=1):
        return {'code': code, 'message': message, 'data': data}

    @staticmethod
    def is_ok(data):
        return int(data['code']) == 0
