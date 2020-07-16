import os
import random
import re
import time

import pyquery
from cloudant import Cloudant
from requests.utils import dict_from_cookiejar, cookiejar_from_dict

from libs.base import BaseClient


class T66y(BaseClient):

    def __init__(self):
        super().__init__()
        self.charset = 'gbk'
        self.base_url = 'http://t66y.com'
        self.page_url = 'thread0806.php?fid=7&search=today'
        self.client = Cloudant.iam(os.environ.get('db_user'), os.environ.get('db_key'), connect=True)
        self.db = self.client[os.environ.get('db_name', 'serverless')]
        self.reply_id = 'pending_reply_list'
        self.day = self.utc_dt.strftime('%Y-%m-%d')

    def _handler(self, username, password, **kwargs):
        for i in range(4):
            result = self.update_cookie(username, password)
            self.log(result['message'])
            if not self.is_ok(result):
                continue

            document = result['data']['document']
            if document['reply_count'] <= 0:
                document[self.reply_id] = []
                document[self.day] = time.strftime('%Y-%m-%d %H:%i:%s')
                document.save()
                break

            time.sleep(random.randint(60, 300))

            pending_reply_list = document[self.reply_id]
            data = random.choice(pending_reply_list)
            result = self.reply(data['tid'], data['title'])
            self.log(result['message'])
            if self.is_ok(result):
                pending_reply_list.remove(data)

                document[self.reply_id] = pending_reply_list
                document['reply_count'] -= 1
                document.save()
            break

    def reply(self, tid, title, content='1024'):
        re_title = f'Re:{title}'
        params = {'atc_autourl': '1', 'atc_usesign': '1', 'atc_convert': '1',
                  'atc_content': content.encode(self.charset, errors='ignore'),
                  'atc_title': re_title.encode(self.charset, errors='ignore'),
                  'tid': tid,
                  'fid': '7',
                  'step': '2', 'action': 'reply', 'pid': '', 'verify': 'verify'
                  }
        html = self.fetch(f'{self.base_url}/post.php?', data=params).text
        if html.find('發貼完畢點擊進入主題列表') != -1:
            return self.success(f'{title} reply done.')
        if html.find('在1024秒內不能發貼') != -1:
            return self.error('1024秒內不能發貼')
        if html.find('用戶組權限') != -1:
            return self.error('用戶組權限：你所屬的用戶組每日最多能發 10 篇帖子')

        if html.find('<html') != -1:
            doc = pyquery.PyQuery(html)
            element = doc('#main div.t').eq(0)
            message = element('center').text()
            if message:
                return self.error(message)
        return self.error(f'{title} reply fail.\n{html}')

    def update_cookie(self, username, password):
        _id = f't66y_{username}'
        if _id not in self.db or self.db[_id]['is_login']:
            result = self.login(username, password)
            if not self.is_ok(result):
                return result

            data = {'cookie': result['data']['cookie'], 'is_login': False, '_id': _id, 'update_time': self.now_time}
            self.db.create_document(data)

        document = self.db[_id]
        self.http.cookies = cookiejar_from_dict(document['cookie'])
        result = self.get_profile()
        self.log(result['message'])
        if not self.is_ok(result):
            document['is_login'] = True
            document.save()
            return self.error(result['message'])

        if self.day in document:
            raise Exception('今天回帖完成.')

        if result['message'].find('俠客') != -1:
            self.send_tg('升级侠客啦')
            raise Exception('升级侠客啦')

        if self.reply_id not in document or len(document[self.reply_id]) <= 0:
            document[self.reply_id] = self.get_pending_reply_list()
            document['reply_count'] = random.randint(6, 10)
            document.save()

        return self.success('', {'document': document})

    def login(self, username, password):
        jump_url = f'{self.base_url}/{self.page_url}'
        params = {'jumpurl': jump_url, 'pwuser': username, 'pwpwd': password, 'forward': jump_url, 'step': 2,
                  'cktime': 86400 * 365}
        res = self.fetch(f'{self.base_url}/login.php', data=params)
        html = res.text
        if html.find('您已經順利登錄') != -1:
            return self.success('login success.', {'cookie': dict_from_cookiejar(res.cookies)})

        if html.find('您登录尝试次数过多') != -1:
            return self.error('您登录尝试次数过多，需要输入验证码才能继续')

        return self.error('login fail.')

    def get_profile(self):
        response = self.fetch(f'{self.base_url}/profile.php', allow_redirects=False)
        if response.status_code != 200:
            return self.error('The cookie has expired')

        doc = pyquery.PyQuery(response.text)
        element = doc('#main .t3').eq(1)
        element = element('table td').eq(0)
        element = element('div.t').eq(1)
        info = element.text()
        return self.success(re.sub(r'\s', ' ', info))

    def get_done_reply_list(self):
        response = self.fetch(f'{self.base_url}/personal.php?action=post')
        doc = pyquery.PyQuery(response.text)
        elements = doc('.t3 div.t .a2')
        tid_list = []
        for element in elements.items():
            href = element.attr('href')
            tid = re.search('tid=([0-9]+)&', href).group(1)
            tid_list.append(tid)
        return tid_list

    def get_pending_reply_list(self):
        pending_post_list = []
        tid_list = self.get_done_reply_list()

        response = self.fetch(f'{self.base_url}/{self.page_url}')
        doc = pyquery.PyQuery(response.text)
        elements = doc('#ajaxtable .tr3')
        for element in elements.items():
            element_a = element('td').eq(1)
            element_a = element_a('a')
            post_url = element_a.attr('href')
            title = element_a.text()
            if title.find('求片求助貼') != -1 or post_url.find('htm_data') == -1:
                continue

            reply_num = int(element('td').eq(3).text())
            if reply_num < 25 or reply_num > 300:
                continue

            # print(reply_num, post_url, title)

            tid_re = re.search('/([0-9]+)\\.html', post_url)
            if not tid_re:
                continue

            tid = tid_re.group(1)
            if tid_list and tid in tid_list:
                continue

            pending_post_list.append({'title': title, 'tid': tid})

        if len(pending_post_list) > 0:
            return pending_post_list

        raise Exception('Not found post.')
