import os
import time
from datetime import datetime, timezone, timedelta
from cloudant import Cloudant

from libs.base import BaseClient


class OneToken(BaseClient):

    def __init__(self):
        super().__init__()
        self._token_url = 'https://login.microsoftonline.com/{}/oauth2/v2.0/token'

    def run(self, **kwargs):
        utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
        bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')

        client = Cloudant.iam(os.environ.get('db_user'), os.environ.get('db_key'), connect=True)
        db = client['db-1']
        for document in db:
            app_data = self.get_ms_token(**document)
            if document['auth_type'] == 'oauth':
                data = self.refresh_token(**document)
                document['access_token'] = data['access_token']
                document['expires_time'] = int(time.time()) + 3500
                document['update_time'] = bj_dt
                if data.get('refresh_token'):
                    document['refresh_token'] = data['refresh_token']
            app_data['expires_time'] = int(time.time()) + 3500
            app_data['update_time'] = bj_dt
            document['app_data'] = app_data
            document.save()
            self.logger.info(f"{document['_id']} refresh done.")
        client.disconnect()

    def refresh_token(self, **kwargs) -> dict:
        default_params = {
            'client_id': kwargs.get('client_id'),
            'redirect_uri': kwargs.get('redirect_uri'),
            'client_secret': kwargs.get('client_secret'),
            'grant_type': 'refresh_token',
            'scope': kwargs.get('scope'),
            'refresh_token': kwargs.get('refresh_token'),
        }
        return self.fetch(self._token_url.format(kwargs.get('tenant_id')), default_params).json()

    def get_ms_token(self, **kwargs):
        tenant_id = kwargs.get('tenant_id')
        url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
        post_data = {
            'grant_type': 'client_credentials',
            'client_id': kwargs.get('client_id'),
            'client_secret': kwargs.get('client_secret'),
            'scope': 'https://graph.microsoft.com/.default'
        }
        return self.fetch(url, data=post_data).json()

    def fetch(self, url, data=None, method=None, **kwargs):
        kwargs.setdefault('timeout', 30)
        if (data or kwargs.get('json')) and method is None:
            method = 'POST'

        if method is None:
            method = 'GET'
        response = self.http.request(method, url, data=data, **kwargs)
        if response.ok:
            return response

        raise Exception(response.url, response.status_code, response.text)
