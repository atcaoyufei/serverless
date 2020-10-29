import logging

import requests

from libs.discuz import Discuz, get_message


class PoJie(Discuz):

    def __init__(self):
        super(PoJie, self).__init__()
        self.base_url = 'https://www.52pojie.cn'
        self.charset = 'gbk'

    def run(self, **kwargs):
        try:
            cookie = 'htVD_2132_connect_is_bind=0; htVD_2132_nofavfid=1; htVD_2132_smile=1D1; htVD_2132_saltkey=Mi6ghKqg; htVD_2132_lastvisit=1602146194; htVD_2132_auth=862cbR%2BENTO7g5VgNsMoyCmUvXkUk%2FsIEKnKr06k9Ymjeu%2Bp9x6yn9zLmoJvaSqk4VKHiux2J7NFCh4MWlNRwao6QbPH; htVD_2132_st_t=1469537%7C1603698873%7Cda2174f7f21192695b6ad655a18c10c8; htVD_2132_forum_lastvisit=D_10_1602726446D_66_1603443681D_24_1603698873; htVD_2132_visitedfid=24D8D66D16D10; htVD_2132_st_p=1469537%7C1603699117%7Ccef46dfe60d5c9d5264384ce6d9b8690; htVD_2132_viewid=tid_1243709; htVD_2132_secqaaqS0=4091010.2a6ef9faa76f96e1e8; htVD_2132_sid=0; htVD_2132_ttask=1469537%7C20201028; htVD_2132_ulastactivity=1603941958%7C0; htVD_2132_lastact=1603941959%09home.php%09spacecp; htVD_2132_checkpm=1; htVD_2132_lastcheckfeed=1469537%7C1603941959'
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
            html = requests.get(f'{self.base_url}/home.php?mod=task&do=draw&id=2',
                                headers={'cookie': cookie, 'referer': self.base_url, 'user-agent': user_agent}).text
            self.logger.info(get_message(html))

        except Exception as e:
            logging.exception(e)
