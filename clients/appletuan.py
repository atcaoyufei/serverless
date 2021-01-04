import re

import pyquery

from libs.base import BaseClient


class AppleTuan(BaseClient):

    def __init__(self):
        super(AppleTuan, self).__init__()
        self.base_url = 'https://www.appletuan.com'

    def run(self, **kwargs):
        try:
            cookie = '_qddaz=QD.qwvb5b.ae718f.kfxdha0c; pgv_pvi=9167585280; tencentSig=1203038208; _ga=GA1.2.360574762.1609401622; _session_id=lxfTdyQ6RRANf%2B2nclpkTbNsHi0BMR5aZoXARRXfGVqNgrxiYCXTevOJTusotttWtJrYkkA9isdo%2BYLlt1v14qZST3yCTx67oJZv%2BhdjGmRGtCCmz1PHVp8hiWK6lQmy4moowM%2B8er6Gc9IWpfz0fmdn%2BdILLf%2F3g74qYv8DauGnc2Aia6xI%2FJTL96NnKthRorYm1LOYojX%2Fbwir8XB%2FBeiIOkf%2FIzOtJru3dBbtSsidhWV%2FPu2ck0nacJAzeuRW4AMO8xvesQHTWXVoMtp9KrUix86p3c%2FP89lLEnUUV0WQPNJiO9XRvwqI4lc1wUoCz6Bth1FhOy%2Fhu%2FRG9J7try5Q6j2cODzB5FObmFdItbp95QGwVLzDQOjO%2BxciBxw58nCcOzj0snmpdTAGfZLem8mrmj%2Bcg6JcEhMPeoR5bnn1--2egKeMb3vWVmRcwq--rqfC50bPIxqTaEydY0oo2g%3D%3D'
            self.headers['Cookie'] = cookie
            self.headers[
                'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
            html = self.fetch(f'{self.base_url}/checkins').text
            if html.find('users/sign_out') == -1:
                self.logger.warning('not login.')
                return

            doc = pyquery.PyQuery(html)

            credit = doc('.w-3\/12').eq(1).text().replace('0.00', '').strip()
            self.logger.info(f'credit -> {credit}')

            token_name = doc('meta[name=csrf-param]').attr('content')
            token = doc('meta[name=csrf-token]').attr('content')

            self.headers['Referer'] = f'{self.base_url}/checkins'
            self.headers[
                'Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
            params = {'_method': 'post', token_name: token}

            response = self.fetch(f'{self.base_url}/checkins/start', data=params)
            doc = pyquery.PyQuery(response.text)
            credit = doc('.w-3\/12').eq(1).text().replace('0.00', '').strip().split('\n')[0]
            self.logger.info(f'credit -> {credit}')
        except Exception as e:
            self.logger.error(e)
