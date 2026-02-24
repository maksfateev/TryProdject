from . import bridgepay

import os

import requests

import random


class Client(bridgepay.Client):
    def __init__(self):
        super().__init__()
        self.api_key = os.environ['BRIDGEPAY_TJ_API_KEY']

    def get_bank_name(self, code, currency='TJS'):
        return super().get_bank_name(code, currency=currency)

    def create_p2p_order(self, amount, *args, **kwargs):
        label = str(random.randint(100000, 999999))
        data = {
            'internalId': label,
            'type': 'in',
            'userId': f'user{random.randint(0, 100)}',
            'amount': str(amount),
            'currency': 'RUB',
            'crossBorderCurrency': 'TJS',
            'paymentOption': 'CROSS_BORDER',
            'notificationUrl': 'https://artbossbot.ru/telegram/bridgepay-tj-callback/',
            'notificationToken': 'Bearer',
            'startDeal': True
        }

        url = self.base_url + '/api/merchant/invoices'
        signature = self.create_signature('POST', url, data)
        headers = {
            'X-Identity': self.api_key,
            'X-Signature': signature
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            print(response.text)

            if len(response.json()['deals']) > 0:
                reqs = response.json()['deals'][0]['requisites']['requisites']
                bank = response.json()['deals'][0]['paymentMethod']
                deal_id = response.json()['deals'][0]['id']

                return {
                    'reqs': reqs,
                    'bank': self.get_bank_name(bank) + ' Таджикистан',
                    'label': deal_id,
                    'deal_id': deal_id
                }

            else:
                raise self.TimeOutException()

        except (requests.exceptions.RequestException, TypeError):
            raise self.RequestException()






