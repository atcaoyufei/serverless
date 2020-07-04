from libs.base import BaseClient


class ZiMuZu(BaseClient):

    def __init__(self):
        super().__init__()
        self.base_url = 'http://www.rrys2020.com'

    def _handler(self, username, password, **kwargs):
        result = self.login(username, password)
        if int(result['status']) != 1:
            self.log(f'login fail\n{result}')
            return
        self.log(f'login success')

        data = self.fetch(f'{self.base_url}/user/login/getCurUserTopInfo').json()
        self.log(data['data']['usercount'])

    def login(self, username, password):
        self.fetch('{}/user/login'.format(self.base_url))
        params = {
            'account': username,
            'password': password,
            'remember': 1,
            'url_back': self.base_url
        }
        self.headers['X-Requested-With'] = 'XMLHttpRequest'
        return self.fetch('{}/User/Login/ajaxLogin'.format(self.base_url), data=params).json()
