import os
from dotenv import load_dotenv

import requests
import json
import hashlib

import random

load_dotenv()


# class Client:
#     def __init__(self):
#         self.base_url = 'https://p2pkassa.online/api'
#         self.api_key = os.environ['P2PKASSA_API_KEY']
#         self.project_id = int(os.environ['P2PKASSA_PROJECT_ID'])

#     def create_headers(self, json_string):
#         auth_token = hashlib.sha512(json_string.encode('utf-8')).hexdigest()
#         return {
#             'Content-Type': 'application/json',
#             'Authorization': f'Bearer {auth_token}'
#         }

#     def create_p2p_order(self, amount, reqs_type, tg_id=1):
#         order_id = random.randint(100000, 999999)
#         data = {
#             'project_id': self.project_id,
#             'order_id': order_id,
#             'amount': amount,
#             'currency': 'RUB',
#             'method': reqs_type,
#             'client_id': str(tg_id)
#         }

#         json_string = f'{self.api_key}{order_id}{self.project_id}{amount:.2f}RUB'
#         headers = self.create_headers(json_string)
#         response = requests.post(self.base_url + '/v3/json', json=data, headers=headers)

#         return response.text

class Client:
    def __init__(self):
        self.base_url = 'https://p2pkassa.online/api'
        self.api_key = os.environ['P2PKASSA_API_KEY']
        self.project_id = int(os.environ['P2PKASSA_PROJECT_ID'])

    class RequestException(Exception):
        pass

    class TimeOutException(Exception):
        pass

    def create_headers(self, join_string):
        auth_token = hashlib.sha512(join_string.encode()).hexdigest()
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {auth_token}'
        }

    def create_p2p_order(self, amount, reqs_type):
        raise self.RequestException()

    def create_pay_link(self, amount):
        label = str(random.randint(100000, 999999))
        data = {
            'project_id': self.project_id,
            'order_id': label,
            'amount': amount,
            'currency': 'RUB'
        }

        join_string = f'{self.api_key}{label}{self.project_id}{amount:.2f}RUB'

        try:
            response = requests.post(
                self.base_url + '/v2/link',
                json=data,
                headers=self.create_headers(join_string)
            )
            data = response.json()

            if 'link' in data.keys():
                return {'link': data['link'].replace('\\', ''), 'label': label}

            raise requests.exceptions.ConnectionError()

        except (
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout
        ):
            raise self.RequestException()

















