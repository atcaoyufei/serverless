import json
import os

from libs.base import BaseClient


class HuaWei(BaseClient):

    def __init__(self):
        super(HuaWei, self).__init__()

    def _handler(self, username, password, **kwargs):
        project = os.environ.get('project')
        login_cmd = f'az login -u {username} -p {password} --allow-no-subscriptions'
        self.logger.info(login_cmd)
        os.system(login_cmd)

        os.system(f'az devops configure --defaults organization=https://dev.azure.com/{project} project={project}')

        data = os.popen('az pipelines list')
        data = json.loads(data.read())
        for i in data:
            os.system(f"az pipelines run --id {i['id']}")