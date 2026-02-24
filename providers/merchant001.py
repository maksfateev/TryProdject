import os
from dotenv import load_dotenv

import requests
import json

import logging


logger = logging.getLogger('REQUISITES')


class Client:
    def __init__(self):
        self.headers = {
            'Authorization': f'Bearer {os.environ["MERCHANT001_API_KEY"]}',
            'Content-Type': 'application/json'
        }
        self.base_url = 'https://api.merchant001.io/v2'

        self.tg_id = None

    class RequestException(Exception):
        pass

    class TimeOutException(Exception):
        pass

    def get_payment_methods(self):
        url = self.base_url + '/payment-method/merchant/available'
        response = requests.get(url, headers=self.headers)

        return response.text

    def create_p2p_order(self, amount, reqs_type, field=None):
        if reqs_type == 'card':
            payment_method = 'any_rub_bank'

        elif reqs_type == 'alfa_monobank':
            payment_method = 'alfa_alfa_sbp'

        else:
            payment_method = 'sbp'

        data = {
            'pricing': {'local': {'amount': int(amount), 'currency': 'RUB'}},
            'selectedProvider': {'method': payment_method},
            'clientId': self.tg_id
        }
        url = self.base_url + '/transaction/merchant'

        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=40)
            print(data, response.text, response.status_code)

            if response.status_code == 201:
                logger.info({'provder': 'merchant001', 'data': response.text})
                data = response.json()

                return {
                    'reqs': data['requisite']['accountNumber'],
                    'bank': data['requisite']['method'],
                    'label': data['transaction']['id']
                }

            elif response.status_code == 404:
                logger.warning({'provder': 'merchant001', 'data': response.text})
                raise self.TimeOutException()

            else:
                logger.error({'provder': 'merchant001', 'data': response.text})
                raise self.RequestException()

        except (requests.exceptions.RequestException, json.decoder.JSONDecodeError, KeyError) as e:
            logger.error({'provder': 'merchant001', 'data': str(e)})
            raise self.RequestException()


