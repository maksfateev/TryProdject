import requests

import os
from dotenv import load_dotenv
load_dotenv()


EMPTY_REQS_MESSAGE = 'provider.P2PCreateInvoice: clientCreateDeal: client.GetDeal: after 10 attempts err: requisite is empty'

class Client:
    def __init__(self):
        self.api_key = os.environ['XPAY_APIKEY']
        self.headers = {'Authorization': f'Bearer {self.api_key}'}
        self.base_url = 'https://api.xpaypro.dev/v1/merchant-api'

    class RequestException(Exception):
        pass

    class TimeOutException(Exception):
        pass

    def create_p2p_order(self, amount, reqs_type):
        bank = 'BANK_ANY'

        if reqs_type == 'card':
            payment_method = 'BANK_CARD'

        else:
            payment_method = 'SBP'

        data = {
            'fiat_currency': 'RUB',
            'fiat_amount': str(amount),
            'crypto_currency': 'USDT',
            'payment_method': payment_method,
            'bank_name': bank
        }

        try:
            response = requests.post(
                self.base_url + '/txs/p2p/invoice',
                headers=self.headers,
                json=data,
                timeout=40
            )
            print(response.text)
            response_data = response.json()

            if 'tx' in response_data.keys():
                return {
                    'reqs': response_data['tx']['payment_requisite'],
                    'bank': response_data['tx']['payment_system'],
                    'label': response_data['tx']['tx_id']
                }

            elif 'message' in response_data.keys() and response_data['message'] == EMPTY_REQS_MESSAGE:
                raise self.TimeOutException()

            raise self.RequestException()

        except (
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout
        ):
            raise self.RequestException()













