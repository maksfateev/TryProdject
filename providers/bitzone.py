import os
from dotenv import load_dotenv

import requests
import json

import random

from django.core.cache import cache

load_dotenv()


class Client:
    def __init__(self):
        self.api_key = os.environ['BITZONE_API_KEY']
        self.base_url = 'https://api.bitzone.space'

    class RequestException(Exception):
        pass

    class TimeOutException(Exception):
        pass

    def create_p2p_order(self, amount, reqs_type, field=None):
        url = self.base_url + '/payment/trading/pay-in'
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key
        }

        if reqs_type == 'alfa_monobank':
            data = {
                'bank': 'ALFA',
                'depositType': 'FTD',
                'transferType': 'local',
                'method': 'sbp',
                'fiatAmount': amount,
                'fiatCurrency': 'RUB'
            }

        elif reqs_type == 'sber_monobank':
            data = {
                'bank': 'sber',
                'depositType': 'FTD',
                'transferType': 'local',
                'method': 'sbp',
                'fiatAmount': amount,
                'fiatCurrency': 'RUB'
            }
    
        elif reqs_type == 'ozon_monobank':
            data = {
                'bank': 'Ozon',
                'depositType': 'FTD',
                'transferType': 'local',
                'method': 'sbp',
                'fiatAmount': amount,
                'fiatCurrency': 'RUB'
            }

        else:
            data = {
                'depositType': 'FTD',
                'transferType': 'local',
                'method': reqs_type,
                'fiatAmount': amount,
                'fiatCurrency': 'RUB'
            }

        try:
            response = requests.post(url, headers=headers, json=data)
            print(response.text, response.status_code)
            response_data = response.json()

            if response_data.get('id') is not None:
                result = {
                    'bank': response_data['requisite']['bank'],
                    'label': response_data['id']
                }

                if reqs_type == 'card':
                    bank = result['bank']
                    if 'амра' in bank.lower():
                        result['reqs'] = f"{response_data['requisite']['requisites']} {response_data['requisite']['ownerName']}"
                    else:
                        result['reqs'] = response_data['requisite']['requisites']

                else:
                    result['reqs'] = response_data['requisite']['sbpNumber']

                return result

            raise self.TimeOutException()

        except (requests.exceptions.RequestException, json.decoder.JSONDecodeError, KeyError):
            raise self.TimeOutException()