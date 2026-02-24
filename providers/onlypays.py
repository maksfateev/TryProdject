import os
from dotenv import load_dotenv

import requests
import json

import random

load_dotenv()


class Client:
    def __init__(self):
        self.api_id = os.environ['ONLYPAYS_API_ID']
        self.secret_key = os.environ['ONLYPAYS_SECRET_KEY']

    class RequestException(Exception):
        pass

    class TimeOutException(Exception):
        pass

    def create_p2p_order(self, amount, reqs_type):
        data = {
            'api_id': self.api_id,
            'secret_key': self.secret_key,
            'amount_rub': int(amount),
            'payment_type': reqs_type
        }
        url = 'https://onlypays.net/get_requisite'

        try:
            response = requests.post(url, json=data, timeout=20)
            print(response.text)
            data = response.json()

            if data['success']:
                return {
                    'reqs': data['data']['requisite'],
                    'bank': data['data']['bank'],
                    'label': data['data']['id']
                }

            else:
                if data['error'] == 'no available requisites':
                    raise self.TimeOutException()

                raise self.RequestException()

        except (
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
            json.decoder.JSONDecodeError,
            KeyError
        ):
            raise self.RequestException()
