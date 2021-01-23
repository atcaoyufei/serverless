import json
import os
import re

import requests

from libs.base import BaseClient


class Az(BaseClient):

    def __init__(self):
        super(Az, self).__init__()
        self.api = 'https://api-atcaoyufei.cloud.okteto.net'

    def _handler(self, username: str, password, **kwargs):
        data = username.split('|')
        project = data[1]
        login_cmd = f'az login --allow-no-subscriptions -u {data[0]} -p {password}'
        self.logger.info(f'{data[0]} login...')
        os.system(login_cmd)

        os.system(f'az devops configure --defaults organization=https://dev.azure.com/{project} project={project}')

        data = os.popen('az pipelines list')
        data = json.loads(data.read())
        for i in data:
            lines = os.popen(f"az pipelines run --id {i['id']}").read()
            run_line = json.loads(lines)
            s = re.search(r'https://dev.azure.com/([a-z]+)/([a-z-0-9]+)/_apis/build/Builds/(\d+)', run_line)
            if s:
                self.logger.info(s.group())
