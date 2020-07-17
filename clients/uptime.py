from concurrent import futures

from libs.discuz import Discuz


class UpTime(Discuz):

    def __init__(self):
        super(UpTime, self).__init__()

    def run(self, **kwargs):
        url_list = kwargs.get('username').split(',')
        self.logger.info(url_list)
        work = min(len(url_list), 3)
        with futures.ThreadPoolExecutor(work) as executor:
            args = ((url,) for url in url_list)
            executor.map(lambda a: self.uptime_check(*a), args)

    def uptime_check(self, url):
        try:
            code = self.fetch(url, timeout=10).status_code
            self.logger.info(f'{url} status code {code}')
        except Exception as e:
            self.logger.warning(e)
