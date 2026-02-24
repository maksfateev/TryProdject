import os
from dotenv import load_dotenv

import requests
import json

import random

load_dotenv()


class Client:
    def __init__(self):
        self.headers = {
            'Authorization': f'Bearer {os.environ["PAYOK_API_KEY"]}',
            'Content-Type': 'application/json'
        }
        self.base_url = 'https://payok.io/api/v2'
        self.shop_id = int(os.environ['PAYOK_SHOP_ID'])
        self.email = os.environ['PAYOK_EMAIL']

    class RequestException(Exception):
        pass

    class TimeOutException(Exception):
        pass

    # def create_pay_link(self, amount):
    #     label = str(random.randint(100000, 999999))
    #     data = {
    #         'amount': int(amount),
    #         'shop': self.shop_id,
    #         'desc': 'Покупка криптоактивов',
    #         'payment': label,
    #         'email': self.email
    #     }
    #     url = self.base_url + '/p2p_payment'

    #     try:
    #         response = requests.post(url, headers=self.headers, json=data, timeout=40)
    #         print(response.text)
    #         data = response.json()

    #         if data.get('status') == 'success':
    #             return {'link': data['data']['link'].replace('\\', ''), 'label': label}

    #         raise requests.exceptions.ConnectionError()

    #     except (
    #         requests.exceptions.ConnectTimeout,
    #         requests.exceptions.ConnectionError,
    #         requests.exceptions.ReadTimeout
    #     ):
    #         raise self.RequestException()
        

    def create_p2p_order(self, amount, reqs_type):
        label = str(random.randint(100000, 999999))
        data = {
            'amount': int(amount),
            'shop': self.shop_id,
            'desc': 'Покупка криптоактивов',
            'payment': label,
            'type': reqs_type,
            'email': self.email
        }
        url = self.base_url + '/p2p_direct'

        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=40)
            print(response.text)
            data = response.json()

            if 'data' in data.keys():
                bank = None

                if reqs_type == 'sbp':
                    bank = data['data']['sbp_bank'].encode().decode('utf-8')

                return {
                    'reqs': data['data']['credentials'],
                    'bank': bank,
                    'label': label,
                    'payok_id': str(data['data']['transaction'])
                }

            else:
                error = data['error_text'].encode().decode('utf-8')

                if error == 'Не удалось получить платеж. Ошибка на стороне Payok':
                    raise self.TimeOutException()

                raise self.RequestException()

        except (
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout
        ):
            raise self.RequestException()





