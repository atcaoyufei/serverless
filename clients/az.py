import json
import os

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
        os.system(login_cmd)

        os.system(f'az devops configure --defaults organization=https://dev.azure.com/{project} project={project}')

        data = os.popen('az pipelines list')
        data = json.loads(data.read())
        for i in data:
            os.system(f"az pipelines run --id {i['id']}")
