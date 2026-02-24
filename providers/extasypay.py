
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
        self.base_url = 'https://api.extasypay.com'
        self.token = os.environ['EXTASYPAY_TOKEN']

    class RequestException(Exception):
        pass

    class TimeOutException(Exception):
        pass

    def _headers(self):
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type':  'application/json',
        }

    def create_p2p_order(self, amount, reqs_type, field=None):
        if reqs_type == 'alfa_monobank':
            url = f"{self.base_url}/api/v1/transactions/internal-sbp"
            payload = {
                'amount': amount,
                'currency': 'RUB',
                'bank_name': 'Альфа-Банк',
                'merchant_transaction_id': str(random.randint(100000, 999999))
            }
            
        elif reqs_type == 'sber_monobank':
            url = f"{self.base_url}/api/v1/transactions/internal-sbp"
            payload = {
                'amount': amount,
                'currency': 'RUB',
                'bank_name': 'СберБанк',
                'merchant_transaction_id': str(random.randint(100000, 999999))
            }

        elif reqs_type == 'ozon_monobank':
            url = f"{self.base_url}/api/v1/transactions/internal-sbp"
            payload = {
                'amount': amount,
                'currency': 'RUB',
                'bank_name': 'Озон Банк',
                'merchant_transaction_id': str(random.randint(100000, 999999))
            }

        else:
            url = f"{self.base_url}/api/v1/transactions/{reqs_type}"
            payload = {
                'amount': amount,
                'currency': 'RUB',
                'merchant_transaction_id': str(random.randint(100000, 999999)),
            }

        print(payload, url, self._headers())

        try:
            response = requests.post(url, headers=self._headers(), json=payload, timeout=40)
            print(payload, response)
            data = response.json()

            if data.get('id') is not None:
                return {
                    'reqs': data.get('card_number') if reqs_type == 'card' else data.get('phone_number'),
                    'bank': data.get('bank_name'),
                    'label': data['id'],
                }

            raise self.TimeOutException()

        except (requests.exceptions.RequestException, json.decoder.JSONDecodeError, KeyError):
            raise self.RequestException()