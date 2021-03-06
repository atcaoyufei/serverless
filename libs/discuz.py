import random
import re
import time

import pyquery
import requests
from requests.cookies import cookiejar_from_dict

from libs.base import BaseClient


def _get_message(html, default_message=None):
    message = re.search(r'<div class="alert_error">([^<]+)<', html)
    if message:
        return message.group(1)
    message = re.search(r'CDATA\[(.*?)<', html)
    if message:
        return message.group(1)

    if default_message:
        return default_message
    return html


def get_message(html, default_message=None):
    doc = pyquery.PyQuery(html)
    return doc('#messagetext > p:nth-child(1)').text() or default_message


class Discuz(BaseClient):

    def __init__(self):
        super(Discuz, self).__init__()

    def user_info(self):
        info_url = f'{self.base_url}/home.php?mod=spacecp&ac=credit&op=base'
        res = self.fetch(info_url, allow_redirects=False)
        if res.status_code != 200:
            raise Exception('The cookie has expired')

        doc = pyquery.PyQuery(res.text)
        html = doc('.creditl').html()
        if html:
            html = html.replace('&#13;', '').strip()
            html = html.replace('<em>', '').replace('</em>', '').replace('(前往兌換商城)', '').strip()
            html = re.sub('<[^>]+>', '', html)
            html = re.sub('(\r?\n)', '', html).strip()
        html = "".join(html.split())
        return self.success(html)

    def views(self):
        uid_list = self.get_users()
        if type(uid_list) != list or len(uid_list) <= 2:
            return None

        view_list = []
        for i in range(11):
            uid = random.choice(uid_list)
            url = f'{self.base_url}/space-uid-{uid}.html'
            self.fetch(url)
            time.sleep(1)
            view_list.append(url)
        return self.success(view_list)

    def get_users(self):
        user_url = f'{self.base_url}/home.php?gender=0&startage=&endage=&avatarstatus=1&username=&searchsubmit=true&op=sex&mod=spacecp&ac=search&type=base'
        html = self.fetch(user_url).text
        doc = pyquery.PyQuery(html)

        message = doc('#messagetext').text()
        if message:
            raise Exception(message)

        elements = doc('ul.buddy li.bbda')
        user_id_list = []
        for element in elements.items():
            link = element('div.avt a').eq(0).attr('href')
            if not link:
                continue
            uid = re.search('uid[=-]([0-9]+)', link)
            if uid:
                user_id_list.append(uid.group(1))
        return user_id_list

    def post(self, **kwargs):
        fid = kwargs.get('fid', 7)
        form_name = kwargs.get('form_name', '#postform')
        post_url = f'{self.base_url}/forum.php?mod=post&action=newthread&fid={fid}'
        res = self.fetch(post_url)

        doc = pyquery.PyQuery(res.text)
        form = doc(form_name)
        input_list = form('input')

        params = {}
        for _input in input_list.items():
            params[_input.attr('name')] = _input.val()
        params['subject'] = kwargs.get('title', '簽到賺積分')
        params['message'] = kwargs.get('content', '簽到賺積分簽到賺積分簽到賺積分簽到賺積分簽到賺積分')
        action = '%s/%s%s' % (self.base_url, form.attr('action').strip('/'), '&inajax=1')
        res = self.fetch(action, params)
        if res.text.find('主題已發佈') != -1:
            return self.success('{} publish done.'.format(params['subject']))

        message = _get_message(res.text)
        return self.error(f'{params["subject"]} publish fail.\n{message}')

    def login2(self, username, password):
        login_url = f"{self.base_url}/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1"
        login_data = {
            "username": username,
            "password": password,
        }
        self.headers['Referer'] = f'{self.base_url}/member.php?mod=logging&action=login'
        response = self.fetch(login_url, data=login_data)
        html = response.text
        _aes = re.findall(r'toNumbers\("([^"]+)"', html, flags=re.S)
        if _aes:
            aes_url = f'https://us-south.functions.cloud.ibm.com/api/v1/web/atcaoyufei_namespace-south/default/aes/?a={_aes[0]}&b={_aes[1]}&c={_aes[2]}'
            # aes_url = f'https://donjs.herokuapp.com/aes/{_aes[0]}/{_aes[1]}/{_aes[2]}'
            aes_cookie = requests.get(aes_url).text
            self.http.cookies = cookiejar_from_dict({'L7DFW': aes_cookie})
            self.fetch(login_url, data=login_data)

        response = self.fetch(f'{self.base_url}/home.php?mod=spacecp&ac=credit')
        html = response.text

        if html.find(username) == -1:
            return self.error(f'login fail.')
        return self.success(f'login success', data={'cookie': response.cookies})

    def login(self, username, password, max_retry=4):
        form = None
        for i in range(1, max_retry):
            res = self.fetch(f'{self.base_url}/member.php?mod=logging&action=login')
            doc = pyquery.PyQuery(res.text)
            form = doc('form[name="login"]')
            if form:
                break

            if i >= max_retry - 1:
                raise Exception('login parse form error', self.base_url)

        action = '%s/%s%s' % (self.base_url, form.attr('action').strip('/'), '&inajax=1')
        input_list = form('input')
        params = {}
        for _input in input_list.items():
            if _input.attr('name'):
                params[_input.attr('name')] = _input.val()
        params['username'] = username
        params['password'] = password
        params['cookietime'] = '2592000'
        params['loginfield'] = 'username'

        response = self.fetch(action, data=params, method='POST')
        html = response.text
        if html.find(username) == -1:
            return self.error(f'login fail.\n{_get_message(html)}')
        return self.success(f'login success', data={'cookie': response.cookies})

    def poke(self, **kwargs):
        uid_list = self.get_users()
        if len(uid_list) <= 2:
            return self.error('not found user.')

        success_text = kwargs.get('success_text', '已發送')
        result = []
        poke_num = kwargs.get('poke_num', 10) + 1
        for i in range(poke_num):
            uid = random.choice(uid_list)
            poke_url = f'{self.base_url}/home.php?mod=spacecp&ac=poke&op=send&uid={uid}'
            res = self.fetch(poke_url)

            doc = pyquery.PyQuery(res.text)
            form = doc('#ct form')
            input_list = form('input')

            params = {}
            for _input in input_list.items():
                params[_input.attr('name')] = _input.val()
            params['iconid'] = '3'

            action = '%s&inajax=1' % poke_url
            res = self.fetch(action, params)
            html = res.text
            if html.find(success_text) != -1:
                result.append(f'{uid} poke done.')
        return self.success('\n'.join(result))

    def sign(self, **kwargs):
        sign_url = '{}/plugin.php?id=dsu_paulsign:sign'.format(self.base_url)
        response = self.fetch(sign_url)
        form_name = kwargs.get('form_name', '#qiandao')
        doc = pyquery.PyQuery(response.text)
        form = doc(form_name)

        if not form:
            return self.error(response.text)

        action = '%s/%s%s' % (self.base_url, form.attr('action').strip('/'), '&inajax=1')

        input_list = form('input')
        params = {}
        for _input in input_list.items():
            params[_input.attr('name')] = _input.val()
        params['todaysay'] = '哈哈哈'
        result = self.fetch(action, params).text
        return self.success(result)
