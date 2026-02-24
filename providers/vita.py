
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
        self.base_url = 'https://vitagrg.online'
        self.token = os.environ['VITA_TOKEN']

    class RequestException(Exception):
        pass

    class TimeOutException(Exception):
        pass

    def _headers(self):
        return {
            'Content-Type': 'application/json',
            'x-api-key': self.token,
        }

    def create_p2p_order(self, amount, reqs_type, field=None):
        url = f"{self.base_url}/api/orders"
        payload = {
            'amount': amount,
            'payment_method': reqs_type,
            'currency': 'RUB',
            'merchant_transaction_id': str(random.randint(100000, 999999)),
            'callback_url': 'https://btcltcbot.tech/telegram/vita-callback/'
        }

        try:
            response = requests.post(url, headers=self._headers(), json=payload, timeout=40)
            data = response.json()

            if data.get('id') is not None:
                return {
                    'reqs': data.get('requisites'),
                    'bank': data.get('bank'),
                    'label': data['id'],
                }

            raise self.TimeOutException()

        except (requests.exceptions.RequestException, json.decoder.JSONDecodeError, KeyError):
            raise self.RequestException()