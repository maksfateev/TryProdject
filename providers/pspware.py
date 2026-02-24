import os
from dotenv import load_dotenv

import requests
import json
import hashlib

import random

load_dotenv()


class Client:
    def __init__(self):
        self.api_key = os.environ['PSPWARE_API_KEY']
        self.merchant_id = os.environ['PSPWARE_MERCHANT_ID']
        self.base_url = 'https://api.pspware.space'

    class RequestException(Exception):
        pass

    class TimeOutException(Exception):
        pass

    def create_sign(self, amount):
        data = f'{float(amount)}:{self.api_key}'
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def create_p2p_order(self, amount, reqs_type, field=None):

        if reqs_type == 'alfa_monobank':
            url = self.base_url + '/merchant/v2/orders'
            headers = {
                'X-API-KEY': self.api_key
            }
            data = {
                'sum': amount,
                'currency': 'RUB',
                'order_type': 'PAY-IN',
                'bank': 'alfabank',
                'pay_types': ['sbp_monobank'],
            }

        elif reqs_type == 'sber_monobank':
            url = self.base_url + '/merchant/v2/orders'
            headers = {
                'X-API-KEY': self.api_key
            }
            data = {
                'sum': amount,
                'currency': 'RUB',
                'order_type': 'PAY-IN',
                'bank': 'sberbank',
                'pay_types': ['sbp_monobank'],
            }

        elif reqs_type == 'ozon_monobank':
            url = self.base_url + '/merchant/v2/orders'
            headers = {
                'X-API-KEY': self.api_key
            }
            data = {
                'sum': amount,
                'currency': 'RUB',
                'order_type': 'PAY-IN',
                'bank': 'ozon',
                'pay_types': ['sbp_monobank'],
            }

        else:
            url = self.base_url + '/payphoria/merchant/api/v1/orders'
            data = {
                'sum': amount,
                'currency': 'RUB',
                'orderType': 'PAY-IN',
                'merchant_id': self.merchant_id,
                'signature': self.create_sign(amount),
                'isSbp': reqs_type == 'sbp'
            }

        try:
            if reqs_type in ['alfa_monobank', 'sber_monobank', 'ozon_monobank']:
                response = requests.post(url, json=data, headers=headers, timeout=40)
            else:
                response = requests.post(url, json=data, timeout=40)
            print(data, response.text)
            response_data = response.json()

            if response_data.get('id') is not None:
                return {
                    'reqs': response_data['card'],
                    'bank': response_data.get('bankName') or response_data.get('bank'),
                    'label': response_data['id']
                }

            raise self.TimeOutException()

        except (requests.exceptions.RequestException, json.decoder.JSONDecodeError, KeyError):
            raise self.RequestException()