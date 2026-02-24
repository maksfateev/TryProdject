import json
import requests

import logging
import datetime

from django.core.cache import cache

import os
from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger('WALLETS')


class Wallet:
    currency = 'BTC'
    network = 'Bitcoin'
    address_regex = '^([13][a-km-zA-HJ-NP-Z1-9]{25,34})|^(bc1([qpzry9x8gf2tvdw0s3jn54khce6mua7l]{39}|[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{59}))$'

    WALLETS_API_KEY = os.environ['B2BWALLET_WALLETS_KEY']
    wallets_headers = {'X-Api-Key': WALLETS_API_KEY}

    API_KEY = os.environ['B2BWALLET_KEY']
    headers = {'X-Api-Key': API_KEY}
    base_url = 'https://b2bwallet.io/api/v1'

    @classmethod
    def get_course(cls):
        course = cache.get(cls.currency)

        if not course:
            url = cls.base_url + '/rates'
            params = {'coin': cls.currency}
            response = requests.get(url, headers=cls.headers, params=params)

            b2b_courses = response.json()

            try:
                rapira_rates = requests.get('https://api.rapira.net/open/market/rates', timeout=5).json()
                usdt_course = 0

                for item in rapira_rates['data']:
                    if item['symbol'] == 'USDT/RUB':
                        usdt_course = item['close']
                        break

                if usdt_course == 0:
                    raise Exception('Null usdt course')

                course = usdt_course * b2b_courses['USD']
                cache.set(cls.currency, course, 120)
                print('rapira')

            except:
                course = b2b_courses['RUB']
                cache.set(cls.currency, course, 120)
                print('b2b')

        return course

    @classmethod
    def get_balance(cls, wallets=False):
        if wallets:
            headers = cls.wallets_headers

        else:
            headers = cls.headers

        url = cls.base_url + '/balance'
        params = {'coin': cls.currency}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=60)

        except requests.exceptions.RequestException:
            return 0.0

        return float(response.json()['balance'])

    @classmethod
    def get_address(cls, wallets=False):
        if wallets:
            headers = cls.wallets_headers

        else:
            headers = cls.headers

        url = cls.base_url + '/address'
        data = {'coin': cls.currency}

        if wallets:
            data['callback_url'] = os.environ['HOST'] + '/telegram/wallet-callback/'

        try:
            response = requests.post(url, headers=headers, json=data, timeout=15)

        except requests.exceptions.RequestException:
            return '⛔️ Ошибка при запросе'

        return response.json()['address']

    @classmethod
    def get_comission(cls, wallets=False):
        if wallets:
            headers = cls.wallets_headers

        else:
            headers = cls.headers

        url = cls.base_url + '/commissions'
        params = {'coin': cls.currency}
        response = requests.get(url, headers=headers, params=params)

        return float(response.json()['withdrawal'])
    
    @classmethod
    def get_comissions(cls, wallets=False):
        if wallets:
            headers = cls.wallets_headers

        else:
            headers = cls.headers

        url = cls.base_url + '/commissions'
        params = {'coin': cls.currency}
        response = requests.get(url, headers=headers, params=params)

        return response.json()

    @classmethod
    def get_transaction(cls, tx_id, wallets=False):
        if wallets:
            headers = cls.wallets_headers

        else:
            headers = cls.headers

        url = cls.base_url + '/transaction'
        params = {'id': tx_id}
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 400:
            status = 'network_error'
            confirmations = 0
        else:
            status = response.json()['status']
            confirmations = 1 if status == 'confirmed' else 0
            
        return {
            'confirmations': confirmations,
            'status': status
        }

    @classmethod
    def get_estimate_fee(cls):
        return 0

    @classmethod
    def send_crypt(cls, address, value, fee, wallets=False):
        if wallets:
            headers = cls.wallets_headers

        else:
            headers = cls.headers

        cache_key = f'{address}:{value}:{cls.currency}'

        if cache.get(cache_key):
            return '⚠️ Повторная отправка'

        url = cls.base_url + '/withdrawal'
        data = {'coin': cls.currency, 'amount': value, 'address': address}

        try:
            response = requests.post(url, headers=headers, json=data, timeout=15)

        except requests.exceptions.RequestException:
            return '⛔️ Ошибка при отправке'

        if response.status_code != 200:
            return response.json()['message']

        tr = response.json()
        result = {
            'amount': value,
            'crypt': cls.currency,
            'address': address,
            'txid': str(tr['id']),
            'tx_link': tr['explorer_link'],
            'fee': float(tr['commission'])
        }
        logger.info({'crypt': cls.currency, 'method': 'send_crypt', 'params': [address, value], 'result': result['txid']})
        cache.set(cache_key, True, 30)

        return result

    @classmethod
    def get_history(cls, wallets=False):
        if wallets:
            headers = cls.wallets_headers

        else:
            headers = cls.headers

        url = cls.base_url + '/history'
        params = {'coin': cls.currency, 'limit': 50}
        response = requests.get(url, headers=headers, params=params)

        history = response.json()['history']
        incomig_txs = []
        outcomig_txs = []

        course = cls.get_course()

        for tr in history:
            history_item = {
                'address': tr['address'],
                'amount': float(tr['amount']),
                'time': datetime.datetime.fromtimestamp(tr['created_at']),
                'crypt': cls.currency,
                'rub_amount': round(float(tr['amount']) * course),
                'txid': str(tr['id'])
            }

            if tr['category'] == 'receive':
                incomig_txs.append(history_item)

            else:
                outcomig_txs.append(history_item)

        return incomig_txs, outcomig_txs

    @classmethod
    def get_transaction_amount(cls, tx_id, wallets=False):
        if wallets:
            headers = cls.wallets_headers

        else:
            headers = cls.headers

        url = cls.base_url + '/transaction'
        params = {'id': tx_id}
        response = requests.get(url, headers=headers, params=params)

        amount = response.json()['amount']

        return amount

    @classmethod
    def get_receive_history(cls, wallets=False):
        if wallets:
            headers = cls.wallets_headers

        else:
            headers = cls.headers

        url = cls.base_url + '/history'
        params = {'coin': cls.currency, 'category': 'receive', 'limit': 100}
        response = requests.get(url, headers=headers, params=params)

        history = response.json()['history']
        incomig_txs = []

        course = cls.get_course()

        for tr in history:
            history_item = {
                'id': str(tr['id']),
                'address': tr['address'],
                'amount': float(tr['amount']),
                'time': datetime.datetime.fromtimestamp(tr['created_at']),
                'crypt': cls.currency,
                'status': tr['status'],
                'rub_amount': round(float(tr['amount']) * course),
                'txid': str(tr['id'])
            }

            incomig_txs.append(history_item)

        return incomig_txs

    @classmethod
    def get_min_deposit(cls, wallets=False):
        if wallets:
            headers = cls.wallets_headers

        else:
            headers = cls.headers

        url = cls.base_url + '/coins'
        response = requests.get(url, headers=headers)
        data = response.json()

        for item in data:
            if item['name'] == cls.currency:
                min_deposit = item['min_deposit'] or 0.0
                return float(min_deposit)

        return 0.0

    @classmethod
    def get_min_withdrawal(cls, wallets=False):
        if wallets:
            headers = cls.wallets_headers

        else:
            headers = cls.headers

        url = cls.base_url + '/coins'
        response = requests.get(url, headers=headers)
        data = response.json()

        for item in data:
            if item['name'] == cls.currency:
                min_withdrawal = item['min_withdrawal'] or 0.0
                return float(min_withdrawal)

        return 0.0
