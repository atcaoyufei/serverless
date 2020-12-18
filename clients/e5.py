import os
import time
from pathlib import Path

import pymongo

from libs.base import BaseClient
from libs.onedrive import OneDrive


class E5(BaseClient):

    def __init__(self):
        super().__init__()
        self.one_drive = OneDrive()

    def run(self, **kwargs):
        client = pymongo.MongoClient(os.environ.get('MONGO_DSN'), connectTimeoutMS=10000)
        db = client.get_database('one_drive')
        col = db.get_collection('one_drive')

        for account in col.find({'one_type': 'e5'}, {'one_type': 0}):
            try:
                self.run_api(account)
            except Exception as e:
                self.logger.error(e)
            break

        client.close()

    def run_api(self, data: dict):
        self.one_drive.access_token = self.one_drive.get_ms_token(**data).get('access_token')
        username = data['username']
        _id = data['_id']

        name = int(time.time())
        new_file = Path(f'{name}.txt')
        new_file.write_text(f'{name}')

        self.one_drive.upload_file(new_file, username)
        self.logger.info(f'{_id}: upload file -> {new_file.name}.')

        new_file.unlink()

        params = {'select': 'id, name, createdDateTime', '$top': 25}
        file_list = self.one_drive.file_list(username, params=params)
        self.logger.info(f"{_id}: file count: {len(file_list['value'])}.")

        if len(file_list['value']) >= 20:
            for file in file_list['value']:
                self.one_drive.delete_file(username, file['name'])

        mail_list = self.one_drive.mail_list(username)
        self.logger.info(f"{_id}: mail count: {len(mail_list['value'])}.")

        site_list = self.one_drive.site_list()
        self.logger.info(f"{_id}: site count: {len(site_list['value'])}.")

        user_list = self.one_drive.user_list()
        user_count = len(user_list['value'])
        self.logger.info(f"{_id}: user count: {user_count}.")

        if user_count > 15:
            for user in user_list['value']:
                if user['userPrincipalName'].find('root') != -1 or user['userPrincipalName'].find('admin') != -1:
                    continue
                self.one_drive.delete_user(user['id'])
        else:
            try:
                user = self.one_drive.create_user()
                self.logger.info(f"{_id} create user -> {user['userPrincipalName']}.")
            except Exception as e:
                self.logger.error(e)

        subscribed_list = self.one_drive.get_subscribed()
        for subscribed in subscribed_list:
            self.logger.info(f"{_id} {subscribed}\n")
