import base64
import logging

from libs.discuz import Discuz


class JkForum(Discuz):

    def __init__(self):
        super(JkForum, self).__init__()
        self.base_url = 'https://www.jkforum.net'

    def run(self, **kwargs):
        try:
            cookie = base64.b64decode(kwargs.get('cookie')).decode('utf-8')
            self.http.headers['Cookie'] = cookie
            try:
                self.log(self.user_info()['message'])
            except Exception as e:
                self.send_tg(str(e))
                return

            self.views()
            self.poke()
            self.sign()
            self.log(self.user_info()['message'])
        except Exception as e:
            logging.exception(e)

    def _handler(self, username, password, **kwargs):
        data = self.login(username, password)
        self.log(data['message'])
        if not self.is_ok(data):
            return
