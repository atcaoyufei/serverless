from libs.discuz import Discuz


class Ck101(Discuz):

    def __init__(self):
        super(Ck101, self).__init__()
        self.base_url = 'https://ck101.com'

    def _handler(self, username, password, **kwargs):
        data = self.login(username, password)
        self.logger.info(data['message'])
        if not self.is_ok(data):
            return

        self.logger.info(self.user_info()['message'])
        self.views()
        self.post(fid=3539)
        self.logger.info(self.user_info()['message'])
