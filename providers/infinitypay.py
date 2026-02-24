import os
from dotenv import load_dotenv

import hmac
import hashlib
import time

import json
import random
import requests


class Client:
    def __init__(self):
        self.token = os.environ['INFINITYPAY_TOKEN']
        self.secret_key = os.environ['INFINITYPAY_SECRET_KEY']
        self.base_url = 'https://api.infinity-pay.io'

    class RequestException(Exception):
        pass

    class TimeOutException(Exception):
        pass        

    def generate_signature(self, raw_signature, secret):
        return hmac.new(secret.encode(), raw_signature.encode(), hashlib.sha256).hexdigest()

    def generate_request_headers(self):
        merchant_token = self.token
        merchant_secret = self.secret_key

        timestamp = int(time.time() * 1000)
        raw_signature = f'{merchant_token}:{timestamp}'
        signature = self.generate_signature(raw_signature, merchant_secret)

        return {
            'x-signature': signature,
            'x-timestamp': str(timestamp),
            'x-merchant-token': merchant_token
        }

    def create_p2p_order(self, amount, reqs_type, **kwargs):
        url = self.base_url + '/v1/pay_in/create'

        if reqs_type == 'alfa_monobank':
            data = {
                'type': 'CIS',
                'amount': amount * 100,
                'm_order_id': str(random.randint(100000, 999999)),
                'pay_method_id': 4,
                'payment_credentials_type': 'phone',
                'callback_url': 'https://btcltcbot.tech/telegram/infinitypay-callback/'
            }

        if reqs_type == 'ozon_monobank':
            data = {
                'type': 'CIS',
                'amount': amount * 100,
                'm_order_id': str(random.randint(100000, 999999)),
                'pay_method_id': 176,
                'payment_credentials_type': 'phone',
                'callback_url': 'https://btcltcbot.tech/telegram/infinitypay-callback/'
            }

        else:
            data = {
                'type': 'CIS',
                'amount': amount * 100,
                'm_order_id': str(random.randint(100000, 999999)),
                'currency_id': 1,
                'payment_credentials_type': 'phone' if reqs_type == 'sbp' else reqs_type,
                'callback_url': 'https://btcltcbot.tech/telegram/infinitypay-callback/'
            }
        headers = self.generate_request_headers()

        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            print(data, response.text)
            response_data = response.json()

            if response_data.get('success') is True:
                return {
                    'reqs': response_data['data']['payment_credentials'][data['payment_credentials_type']],
                    'bank': response_data['data']['pay_method']['name'],
                    'label': response_data['data']['order_hash']
                }

            raise self.TimeOutException()

        except (requests.exceptions.RequestException, json.decoder.JSONDecodeError, KeyError):
            raise self.RequestException()
