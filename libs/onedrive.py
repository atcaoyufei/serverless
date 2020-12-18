import json
import logging
import random
import string
from pathlib import Path
from urllib.parse import urlencode

import requests

SKU_MAP = {
    '94763226-9b3c-4e75-a931-5c89701abe66': 'A1教职',
    '314c4481-f395-4525-be8b-2ec4bb1e9d91': 'A1学生',
    '6fd2c87f-b296-42f0-b197-1e91e994b900': 'Office 365 E3',
    'c42b9cae-ea4f-4ab7-9717-81576235ccac': 'Office 365 E5'
}


def _get_drive(username, site=False):
    drive = f'/users/{username}/drive/root'
    if site:
        drive = f'/sites/{username}/drive/root'
    return drive


class OneDrive:

    def __init__(self):
        self._api_base_url = 'https://graph.microsoft.com/v1.0/'
        self.http = requests.session()
        self._auth_url = 'https://login.microsoftonline.com/{}/oauth2/v2.0/authorize'
        self._token_url = 'https://login.microsoftonline.com/{}/oauth2/v2.0/token'
        self.access_token = None
        self._redirect_uri = 'https://pydrive.github.io'
        self._scope = 'offline_access Sites.ReadWrite.All Directory.ReadWrite.All Directory.AccessAsUser.All'
        self.logger = logging.getLogger(self.__class__.__name__)
        self.file_fields = 'id, name, size, folder, audio, video, photo, image, createdDateTime, lastModifiedDateTime'

    def api(self, api_sub_url, params=None, data=None, method=None, **kwargs):
        self.http.headers['Authorization'] = "Bearer {}".format(self.access_token)
        if api_sub_url.find('http') == -1:
            url = '{}/{}'.format(self._api_base_url.strip('/'), api_sub_url.strip('/'))
        else:
            url = api_sub_url
        response = self.fetch(url, data=data, method=method, params=params, **kwargs)
        if response.status_code == 204:
            return {'status_code': response.status_code}
        if len(response.content) > 1:
            return response.json()
        return {'status_code': response.status_code}

    def api_debug(self, api_sub_url, params=None, data=None, method=None, **kwargs):
        return json.dumps(self.api(api_sub_url, params, data, method, **kwargs), indent=4)

    def site_list(self):
        api_params = {'search': '*', '$top': 20, '$select': 'id, webUrl, displayName'}
        return self.api('/sites', api_params)

    def mail_list(self, username):
        api_params = {'$select': 'id, subject', '$top': 10}
        return self.api(f'/users/{username}/messages', api_params)

    def upload_file(self, file, username, site=False, **kwargs):
        drive = _get_drive(username, site)
        p = Path(file)
        return self.api(f'{drive}:/{p.name}:/content', method='PUT', data=p.read_bytes())

    def file_list(self, username, site=False, folder=None, fields=None, limit=20, **kwargs):
        dest = '/children'
        if folder and folder != '/':
            dest = ':/{}:/children'.format(folder)

        drive = _get_drive(username, site)
        if not fields:
            fields = self.file_fields

        params = {'select': fields, '$top': limit, '$expand': 'thumbnails($select=large)'}
        params.update(kwargs)
        return self.api(f'{drive}{dest}', params)

    def delete_file(self, username, file, site=False, **kwargs):
        drive = _get_drive(username, site)
        return self.api(f'{drive}:/{file}', method='DELETE', timeout=10)

    def get_file(self, username, file, site=False, **kwargs):
        drive = _get_drive(username, site)
        return self.api(f'{drive}:/{file}', params={'$select': 'id,@microsoft.graph.downloadUrl'})

    def enabled_user(self, user, status=True):
        post_data = {
            'accountEnabled': status,
            'usageLocation': 'HK',
        }
        return self.api(f'/users/{user}', json=post_data, method='PATCH')

    def password(self, user, password=None):
        if not password:
            password = random.choices(string.ascii_letters + string.digits + '!#$%&()*+-/:;<=>?@', k=10)

        post_data = {'passwordProfile': {
            'password': password,
            'forceChangePasswordNextSignIn': False,
            'passwordPolicies': 'DisablePasswordExpiration, DisableStrongPassword'
        }}

        return self.api(f'/users/{user}', json=post_data, method='PATCH')

    def create_user(self, **kwargs):
        _subscribed = random.choice(self.get_subscribed())
        domain = self.get_default_domain()
        password = kwargs.get('password')
        if not password:
            password = ''.join(random.choices(string.ascii_letters + string.digits + '!#$%&()*+-/:;<=>?@', k=10))

        username = kwargs.get('username', ''.join(random.choices(string.ascii_letters, k=6)))
        user_email = f'{username}@{domain}'
        post_data = {
            'accountEnabled': True,
            'displayName': username,
            'mailNickname': username,
            'passwordPolicies': 'DisablePasswordExpiration, DisableStrongPassword',
            'passwordProfile': {
                'password': password,
                'forceChangePasswordNextSignIn': False
            },
            'userPrincipalName': user_email,
            'usageLocation': 'HK'
        }
        data = self.api('/users', json=post_data, method='POST')

        subscribed_list = self.get_subscribed()
        if len(subscribed_list) > 1:
            random.shuffle(subscribed_list)

        for subscribed in subscribed_list:
            sku_id = subscribed.get('sku_id')
            if sku_id == '6470687e-a428-4b7a-bef2-8a291ad947c9':
                continue
            self.assign_license(user_email, sku_id)
            break
        return data

    def assign_license(self, user_email, sku_id, **kwargs):
        api = f'/users/{user_email}/assignLicense'
        post_data = {
            'addLicenses': [
                {
                    'disabledPlans': [],
                    'skuId': sku_id
                }
            ],
            'removeLicenses': []
        }
        return self.api(api, json=post_data)

    def get_default_domain(self, **kwargs):
        data = self.api('/domains')
        for item in data['value']:
            if item.get('isDefault'):
                return item.get('id')
        return None

    def get_domains(self, **kwargs):
        return self.api('/domains')

    def get_subscribed(self):
        subscribed_list = self.api('/subscribedSkus')
        result = []
        for i in subscribed_list['value']:
            if i['capabilityStatus'] == 'Enabled':
                sku_name = SKU_MAP.get(i['skuId'], i['skuId'])
                result.append({'status': i['capabilityStatus'], 'sku_id': i['skuId'], 'sku_name': sku_name,
                               'units': f'{i["consumedUnits"]}/{i["prepaidUnits"]["enabled"]}'})
        return result

    def user_list(self, **kwargs):
        params = {'$select': 'id,displayName,accountEnabled,userPrincipalName,assignedLicenses',
                  '$top': 20}
        params.update(kwargs)
        return self.api('/users', params=params)

    def delete_user(self, user):
        return self.api(f'/users/{user}', method='DELETE')

    def get_user(self, user):
        params = {'$expand': 'memberOf'}
        self._api_base_url = self._api_base_url.replace('v1.0', 'beta')
        return self.api(f'/users/{user}', params=params)

    def get_role(self, user):
        params = {'$expand': 'directReports'}

        return self.api(f'/users/{user}', params=params)

    def get_disabled_users(self):
        return self.user_list(filter='accountEnabled eq false')

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

    def authorize_url(self, **kwargs):
        default_params = {
            'client_id': kwargs.get('client_id'),
            'redirect_uri': self._redirect_uri,
            'response_type': 'code',
            'state': 'debug',
            'scope': self._scope,
            'prompt': 'consent'
        }
        return '{}?{}'.format(self._auth_url.format(kwargs.get('tenant_id')), urlencode(default_params, doseq=True))

    def fetch_token(self, **kwargs) -> dict:
        default_params = {
            'client_id': kwargs.get('client_id'),
            'redirect_uri': self._redirect_uri,
            'client_secret': kwargs.get('client_secret'),
            'grant_type': 'authorization_code',
            'scope': self._scope,
            'code': kwargs.get('code'),
        }
        return self.fetch(self._token_url.format(kwargs.get('tenant_id')), default_params).json()

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
