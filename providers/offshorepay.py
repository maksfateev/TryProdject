import os
from dotenv import load_dotenv
import requests
import json
import hashlib
import hmac
import base64
import random
load_dotenv()


class Client:
    def __init__(self):
        self.api_key = os.environ['OFFSHOREPAY_API_KEY']
        self.merchant_id = os.environ['OFFSHOREPAY_MERCHANT_ID']
        self.base_url = 'https://offshorepay.org'

    class RequestException(Exception):
        pass

    class TimeOutException(Exception):
        pass

    def create_p2p_order(self, amount, reqs_type, field=None):
        label = str(random.randint(100000, 999999))
        # if reqs_type == 'alfa_monobank':
        #     data = {
        #         'external_id': label,
        #         'merchant_id': self.merchant_id_mono,
        #         'amount': str(amount),
        #         'self-bank': True,
        #         "payment_gateway": "Alfa_rub",
        #         'callback_url': 'https://bitmagnit.tech.ru/telegram/offshorepay-callback/',
        #     }
        # else:
        data = {
            'external_id': label,
            'merchant_id': self.merchant_id,
            'amount': str(amount),
            'currency': 'rub',
            'payment_detail_type': 'phone' if reqs_type == 'sbp' else 'card',
            'callback_url': 'https://bitmagnit.tech/telegram/offshorepay-callback/',
        }
        url = self.base_url + '/api/h2h/order'
        headers = {
            'Accept': 'application/json',
            'Access-Token': self.api_key
        }
        print(data)
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response_data = response.json()
            print(response_data)

            if 'message' not in response_data.keys() and response_data['success']:
                tr_id = response_data['data']['order_id']

                return {
                    'reqs': response_data['data']['payment_detail']['detail'],
                    'bank': response_data['data']['payment_gateway_name'],
                    'label': tr_id,
                }
            raise self.RequestException()
        except (
            json.decoder.JSONDecodeError,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
            TypeError
        ):
            raise self.RequestException()