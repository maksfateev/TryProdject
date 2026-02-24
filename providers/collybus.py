import os
from dotenv import load_dotenv

import requests
import json

import random

from django.core.cache import cache

load_dotenv()


class Client:
    def __init__(self):
        self.token = os.environ['COLLYBUS_API_KEY']
        self.base_url = 'https://collybus.biz'

    class RequestException(Exception):
        pass

    class TimeOutException(Exception):
        pass

    def create_p2p_order(self, amount, reqs_type, field=None):
        url = self.base_url + '/api/orders'
        headers = {
            'X-Api-Key': self.token,
        }

        if reqs_type == 'alfa_monobank':
            data = {
                'amount': str(amount),
                'payment_method': "alfa-alfa",
                'currency': "RUB",
                'internal_id': str(random.randint(100000, 999999)),
                'callback_url': 'https://btcltcbot.tech/telegram/collybus-callback/'
            }

        else:
            data = {
                'amount': str(amount),
                'payment_method': reqs_type,
                'currency': "RUB",
                'internal_id': str(random.randint(100000, 999999)),
                'callback_url': 'https://btcltcbot.tech/telegram/collybus-callback/'
            }

        try:
            response = requests.post(url, headers=headers, json=data)
            print(data, url, headers)
            print(response.text, response.status_code)
            response_data = response.json()

            if response_data.get('id') is not None:
                return {
                    'reqs': response_data['requisites'],
                    'bank': response_data['bank'],
                    'label': response_data['id']
                }

            raise self.TimeOutException()

        except (requests.exceptions.RequestException, json.decoder.JSONDecodeError, KeyError):
            raise self.TimeOutException()
