import logging

from libs.discuz import Discuz, get_message


class PoJie(Discuz):

    def __init__(self):
        super(PoJie, self).__init__()
        self.base_url = 'https://www.52pojie.cn'
        self.charset = 'gbk'

    def run(self, **kwargs):
        try:
            try:
                self.logger.info(self.user_info()['message'])
            except Exception as e:
                self.send_tg(f"{self.__class__.__name__}\n{str(e)}")
                return

            self.headers['Referer'] = 'https://www.52pojie.cn/home.php?mod=spacecp&ac=credit&showcredit=1'
            html = self.fetch(f'{self.base_url}/home.php?mod=task&do=draw&id=2').text
            self.logger.info(get_message(html))
            self.logger.info(self.user_info()['message'])
        except Exception as e:
            logging.exception(e)
