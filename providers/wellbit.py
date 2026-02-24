import os
from dotenv import load_dotenv

import requests
import json
import random
import hashlib

from django.core.cache import cache

load_dotenv()


class Client:
    def __init__(self):
        self.token = os.environ['WELLBIT_TOKEN']
        self.private_key = os.environ['WELLBIT_PRIVATE_KEY']
        self.user_login = os.environ['WELLBIT_USER_LOGIN']
        self.user_id = os.environ['WELLBIT_USER_ID']
        self.base_url = 'https://wellbit.pro/api'

    class RequestException(Exception):
        pass

    class TimeOutException(Exception):
        pass

    def create_p2p_order(self, amount, reqs_type, field=None):
        secret_str = f"{self.private_key}{self.user_login}{self.user_id}"
        secret = hashlib.md5(secret_str.encode('utf-8')).hexdigest()

        url = self.base_url + '/payment/make'
        headers = {
            'Content-Type': 'application/json',
            'token': self.token,
            'secret': secret
        }
        data = {
            'currency': 'RUB',
            'amount': amount,
            'credential_type': reqs_type,
            'bank_code': 'ANY',
            'credential_require': 'yes',
            'merchant_transaction_id': str(random.randint(100000, 999999)),
            'return_url': field or '',
            'client_ip': '192.168.1.1',
            'client_email': 'user@example.com',
            'client_phone': '89991234567',
            'client_username': 'ivan_ivanov',
            'include_fee': 'no',
            'card_from_number': '1234567890123456',
            'card_from_fio': 'Иван Иванов'
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            print(response.text, response.status_code)
            response_data = response.json()

            if isinstance(response_data, list) and response_data:
                response_data = response_data[0]

            payment = response_data.get('payment', {})
            if payment.get('id') is not None:
                return {
                    'id': payment['id'],
                    'bank': payment.get('credential'),
                    'reqs': payment.get('credential_additional_bank')
                }

            raise self.TimeOutException()

        except (requests.exceptions.RequestException, json.decoder.JSONDecodeError, KeyError) as e:
            raise self.TimeOutException()
