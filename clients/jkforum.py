import base64

from requests.cookies import cookiejar_from_dict

from libs.discuz import Discuz


class JkForum(Discuz):

    def __init__(self):
        super(JkForum, self).__init__()
        self.base_url = 'https://www.jkforum.net'

    def run(self, **kwargs):
        try:
            cookie = base64.b64decode(kwargs.get('cookie'))
            self.http.cookies = cookiejar_from_dict(cookie)
            try:
                self.log(self.user_info()['message'])
            except Exception as e:
                self.send_tg(str(e))
                return

            self.views()
            self.log(self.poke()['message'])
            self.log(self.sign()['message'])
            self.log(self.user_info()['message'])
        except Exception as e:
            print(e)

    def _handler(self, username, password, **kwargs):
        data = self.login(username, password)
        self.log(data['message'])
        if not self.is_ok(data):
            return
