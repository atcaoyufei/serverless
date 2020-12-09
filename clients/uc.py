import pyquery

from libs.base import BaseClient


class Uc(BaseClient):

    def __init__(self):
        super(Uc, self).__init__()
        self.base_url = 'https://uclub.ucloud.cn'

    def _handler(self, username, password, **kwargs):
        data = self.login(username, password)
        self.logger.info(f'{username}: {data}')
        credit = self.get_credit()
        self.logger.info(self.sign())
        new_credit = self.get_credit()
        self.logger.info(f'{credit} -> {new_credit}')

    def sign(self):
        response = self.fetch(f'{self.base_url}/index/signin/dosign.html', method='POST')
        doc = pyquery.PyQuery(response.text)
        return doc('.system-message h1').text()

    def get_credit(self) -> int:
        response = self.fetch(f'{self.base_url}/index/user/index.html')
        doc = pyquery.PyQuery(response.text)
        return doc('a.viewscore').text()

    def login(self, username, password):
        login_url = f'{self.base_url}/index/user/login.html'
        response = self.fetch(login_url)
        doc = pyquery.PyQuery(response.text)
        token = doc('input[name="__token__"]').val()
        data = {
            "__token__": token,
            "account": username,
            "password": password,
            "keeplogin": "1"
        }
        response = self.fetch(login_url, data=data)
        doc = pyquery.PyQuery(response.text)
        return doc('.system-message h1').text().strip()
