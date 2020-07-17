from libs.discuz import Discuz


class UpTime(Discuz):

    def __init__(self):
        super(UpTime, self).__init__()

    def run(self, **kwargs):
        url_list = [
            'http://pyindex.live/',
            'http://caoyufei.bplaced.net/',
            'http://web.coayufei.usw1.kubesail.io/env',
            'https://0001.us-south.cf.appdomain.cloud/'
        ]
        for url in url_list:
            try:
                self.logger.info(url, 'http code:', self.fetch(url, timeout=10).status_code)
            except Exception as e:
                self.logger.info(e)
