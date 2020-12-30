import re

import pyquery

from libs.base import BaseClient


class AppleTuan(BaseClient):

    def __init__(self):
        super(AppleTuan, self).__init__()
        self.base_url = 'https://www.appletuan.com'

    def run(self, **kwargs):
        try:
            cookie = '_qddaz=QD.qwvb5b.ae718f.kfxdha0c; pgv_pvi=9167585280; tencentSig=1203038208; _session_id=4rVjFLRnK9ZnWfqxVTxhoNSEDxFXNPanATmEuHe18Jcx2%2FhUEuzdrrXgSOCSOdguPsN87CCSgtVGGkC3GsGn56XEAFv8eWBnUG9Rk7WO03RLi56B3vPZuZQ0qQ3nT9IVfAUHeKiEC28BuQqLu1njrT%2BaveX4mudPiaBauiRJwsUfNWTjnPysBCuwAUTucszJpVjI2VSJGyE30%2FBejTgJMPlJHNwtUaP1eMJhwkLNVCute%2FEqm%2Fs5ExMCdcgBcVAq9byYTzB3bXWB14n4qVrskg1HFbFtXdpCVAtth%2BFOiqmXyQ1fJiJCyDHGR6E1OS07f9001j3tZgJaCShVLt8DXyDBCgwGTzm3oyfac1WMXYJOnT4td%2BPgnzDUWsXACVSuF0bM7de42XYEgYtW3BPchDafFORCRi23mx7PSxhCUpmf--lNfKIQQ9dnpiQmQU--Yd%2BL8JfrdffsEHq4V1LYdg%3D%3D'
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

            self.headers['Referer'] = 'https://www.appletuan.com/checkins'
            self.headers[
                'Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
            params = {'_method': 'post', token_name: token}

            response = self.fetch(f'https://www.appletuan.com/checkins/start', data=params)
            doc = pyquery.PyQuery(response.text)
            credit = doc('.w-3\/12').eq(1).text().replace('0.00', '').strip().split('\n')[0]
            self.logger.info(f'credit -> {credit}')
        except Exception as e:
            self.logger.error(e)
