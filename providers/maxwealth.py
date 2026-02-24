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
        self.api_key = os.environ['MAXWEALTH_API_KEY']
        self.base_url = 'https://maxwealth.io/api/v1'

    class RequestException(Exception):
        pass

    class TimeOutException(Exception):
        pass

    def create_p2p_order(self, amount, reqs_type, field=None):
        url = self.base_url + '/wallet'
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        data = {
            'payment': {'code': 'meta_bank'},
            'partner_request': {'id': str(random.randint(100000, 999999))},
            'sum': {'currency_code': 'RUR', 'amount': amount},
            'payment_method': reqs_type.upper(),
            'is_multi': False
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            print(response.text)
            response_data = response.json()

            if 'error' in response_data.keys():
                raise self.TimeOutException()

            return {
                'reqs': response_data['result']['wallet']['number'],
                'bank': response_data['result']['wallet'].get('bank'),
                'label': response_data['result']['request']['id']
            }

        except (requests.exceptions.RequestException, json.decoder.JSONDecodeError, KeyError):
            raise self.RequestException()
