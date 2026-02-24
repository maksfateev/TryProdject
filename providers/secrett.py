import os
from dotenv import load_dotenv

import requests
import json

import random

from django.core.cache import cache

load_dotenv()


class Client:
    def __init__(self):
        self.login = os.environ['SECRETT_LOGIN']
        self.passphrase = os.environ['SECRETT_PASSPHRASE']
        self.account_id = os.environ['SECRETT_ACCOUNT_ID']
        self.api_key = os.environ['SECRETT_API_KEY']
        self.base_url = 'https://api.secrett.net'

    class RequestException(Exception):
        pass

    class TimeOutException(Exception):
        pass

    def get_token(self):
        token = cache.get('secrett-token')

        if token is None:
            url = self.base_url + '/api/client/auth/login'
            data = {
                'login': self.login,
                'passphrase': self.passphrase
            }
            response = requests.post(url, json=data, timeout=15)
            token = {'access': response.json()['accessToken'], 'secret': response.json()['secretKey']}

            cache.set('secrett-token', token, 60 * 60 * 12)

        return token

    def create_p2p_order(self, amount, reqs_type, field=None):
        token = self.get_token()

        url = self.base_url + f'/api/client/orders/deposit?accountId={self.account_id}'
        headers = {
            'Authorization': f'Bearer {token["access"]}',
            'X-Secret-Key': token['secret'],
            'X-Store-Key': self.api_key
        }
        data = {
            'useFastPayment': reqs_type == 'sbp',
            'value': str(amount),
            'externalId': str(random.randint(100000, 999999)),
            'webhookUrl': 'https://btcltcbot.tech/telegram/secrett-callback/'
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=20)
            print(response.text)
            response_data = response.json()

            if response_data.get('orderId') is not None:
                return {
                    'reqs': response_data.get('contactNumber') if reqs_type == 'sbp' else response_data.get('accountNumber'),
                    'bank': response_data['bankName'],
                    'label': response_data['orderId'],
                    'request_id': data['externalId']
                }

            raise self.TimeOutException()

        except (requests.exceptions.RequestException, json.decoder.JSONDecodeError, KeyError):
            raise self.RequestException()