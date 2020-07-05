from libs.discuz import Discuz


class UpTime(Discuz):

    def __init__(self):
        super(UpTime, self).__init__()

    def run(self, **kwargs):
        url_list = ['http://pyindex.live/', 'http://caoyufei.bplaced.net/', 'https://zzcworld.com/']
        for url in url_list:
            try:
                self.log(url, 'http code:', self.fetch(url, timeout=10).status_code)
            except Exception as e:
                self.log(e)
