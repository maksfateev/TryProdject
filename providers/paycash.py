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
        self.base_url = 'https://api.paycash.ac'
        self.access_token = os.environ['PAYCASH_ACCESS_TOKEN']
        self.secret_token = os.environ['PAYCASH_SECRET_TOKEN']

    class RequestException(Exception):
        pass

    class TimeOutException(Exception):
        pass

    def _headers(self):
        return {
            'X-Access-Token': self.access_token,
            'X-Secret-Token': self.secret_token,
            'Content-Type':  'application/json',
        }

    def create_p2p_order(self, amount, reqs_type, field=None):
        url = f"{self.base_url}/api/v1/create-order/"
        match reqs_type:
            case 'card':
                payment_method = 'CARD'
            case 'sbp':
                payment_method = 'SBP'
            case 'alfa_monobank':
                payment_method = 'ALFA'
            case 'sber_monobank':
                payment_method = 'SBER'
            case 'tbank_monobank':
                payment_method = 'TBANK'
            case 'psb_monobank':
                payment_method = 'PSBBANK'
            case 'ozon_monobank':
                payment_method = 'OZON'
            case 'gazprom_monobank':
                payment_method = 'GAZPROM'
            case 'bt':
                payment_method = 'BT'
        
        payload = {
            'amount': amount,
            'currency': 'RUB',
            'payment_method': payment_method,
            'merchant_transaction_id': str(random.randint(100000, 999999))
        }

        print(payload, url, self._headers())

        try:
            response = requests.post(url, headers=self._headers(), json=payload, timeout=30)
            data = response.json()
            print(data)

            if data.get('id') is not None:
                return {
                    'reqs': data['requisites']['requisites'],
                    'bank': data['requisites']['bank_name'],
                    'label': data['id'],
                }

            raise self.TimeOutException()

        except (requests.exceptions.RequestException, json.decoder.JSONDecodeError, KeyError):
            raise self.RequestException()