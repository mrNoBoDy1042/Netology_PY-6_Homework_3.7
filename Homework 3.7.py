from pprint import pprint
from urllib.parse import urlencode, urljoin

import requests

AUTHORIZE_URL = 'https://oauth.yandex.ru/authorize'
APP_ID = 'f8769f4b300947ecba3ccd9eec93c00f'

auth_data = {
    'response_type': 'token',
    'client_id': APP_ID
}

print('?'.join((AUTHORIZE_URL, urlencode(auth_data))))


TOKEN = 'insert your token here'

class YMBase:
    MANAGEMENT_URL = 'https://api-metrika.yandex.ru/management/v1/'
    STAT_URL = 'https://api-metrika.yandex.ru/stat/v1/data'

    def get_headers(self):
        return {
            'Authorization': 'OAuth {}'.format(self.token),
            'User-Agent': 'Netology 6 homework',
            'Content-Type': 'application/x-yametrika+json'
        }


class YaMetrica(YMBase):
    def __init__(self, token):
        self.token = token
        # super().__init__()

    def get_counters(self):
        url = urljoin(self.MANAGEMENT_URL, 'counters')
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        return [
            Counter(self.token, counter_id['id']) for counter_id in response.json()['counters']
        ]

# Создание счетчика
# При выполнении возвращает ошибку 400:
#     'message': "Could not read JSON Unrecognized token 'counter': was expecting "
#     "('true', 'false' or 'null')\n"
#     ' at [Source: counter=name&counter=site; line: 1, column: 8]'
    def create_counter(self, counter_name, site):
        url = urljoin(self.MANAGEMENT_URL, 'counters')
        data = {
            "counter": {
                "name": counter_name,
                "site": site,
            }
        }
        headers = self.get_headers()
        response = requests.post(url, headers=headers, data=data)
        return response.json()


class Counter(YMBase):
    def __init__(self, token, counter_id):
        self.token = token
        self.counter_id = counter_id

    def get_info(self):
        url = urljoin(self.MANAGEMENT_URL, 'counter{}'.format(self.counter_id))
        headers = self.get_headers()
        response = requests.get(url, headers=headers)
        return response.json()

    @property
    def visits(self):
        headers = self.get_headers()
        params = {
            'id': self.counter_id,
            'metrics': 'ym:s:visits'
        }
        response = requests.get(self.STAT_URL, params, headers=headers)
        return response.json()['totals'][0]

    @property
    def views(self):
        headers = self.get_headers()
        params = {
            'id': self.counter_id,
            'metrics': 'ym:s:pageviews'
        }
        response = requests.get(self.STAT_URL, params, headers=headers)
        return response.json()['data'][0]['metrics'][0]

    @property
    def users(self):
        headers = self.get_headers()
        params = {
            'id': self.counter_id,
            'metrics': 'ym:s:users',
        }
        response = requests.get(self.STAT_URL, params, headers=headers)
        return response.json()['data'][0]['metrics'][0]

ym = YaMetrica(TOKEN)
counters = ym.get_counters()
pprint(ym.create_counter('test', 'https://mrnobody1042.github.io/'))
for counter in counters:
    pprint(counter.visits)
    pprint(counter.users)
