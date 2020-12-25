from libs.discuz import Discuz


class Hostloc(Discuz):

    def __init__(self):
        super(Hostloc, self).__init__()
        self.base_url = 'https://www.hostloc.com'

    def _handler(self, username, password, **kwargs):
        data = self.login2(username, password)
        self.logger.info(data['message'])
        if not self.is_ok(data):
            return

        self.logger.info(self.user_info()['message'])
        self.views()
        message = self.user_info()['message']
        self.logger.info(f'{username}: {message}')

