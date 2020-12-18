import logging

from libs.discuz import Discuz


class JkForum(Discuz):

    def __init__(self):
        super(JkForum, self).__init__()
        self.base_url = 'https://www.jkforum.net'

    def run(self, **kwargs):
        try:
            try:
                self.logger.info(self.user_info()['message'])
            except Exception as e:
                self.logger.error(f"{self.__class__.__name__}\n{str(e)}")
                return

            self.views()
            self.poke()
            self.sign()
            self.logger.info(self.user_info()['message'])
        except Exception as e:
            logging.exception(e)

    def _handler(self, username, password, **kwargs):
        data = self.login(username, password)
        self.logger.info(data['message'])
        if not self.is_ok(data):
            return
