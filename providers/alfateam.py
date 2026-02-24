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
        self.api_key = os.environ['ALFATEAM_API_KEY']
        self.secret_key = os.environ['ALFATEAM_SECRET_KEY']
        self.base_url = 'https://api.alfateam.cloud'
    
    class RequestException(Exception):
        pass
    
    class TimeOutException(Exception):
        pass

    def create_signature(self, method, url, data):
        sign_string = '{0}{1}{2}'.format(method, url, json.dumps(data))
        signature = base64.b64encode(
            hmac.new(self.secret_key.encode(), sign_string.encode(), hashlib.sha1).digest()
        ).decode()
        return signature
    
    def create_p2p_order(self, amount, reqs_type, field=None):
        if reqs_type == 'card':
            reqs_type = 'TO_CARD'
        else:
            reqs_type = 'SBP'
        label = str(random.randint(100000, 999999))
        data = {
            'type': 'in',
            'amount': str(amount),
            'currency': 'RUB',
            'notificationUrl': 'https://btcltcbot.tech/telegram/alfateam-callback/',
            'notificationToken': 'Bearer',
            'internalId': label,
            'userId': f'user{random.randint(0, 100)}',
            'paymentOption': reqs_type,
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
            response_data = response.json()
            if 'id' in response_data.keys():
                tr_id = response_data['id']
                # response = requests.get(
                #     self.base_url + f'/api/merchant/invoices/{tr_id}/available-payment-variants',
                #     headers=headers
                # )
                # payment_methods = response.json()

                # if len(payment_methods) == 0:
                #     raise self.TimeOutException()
                
                # payment_method = None
                # bank = None
                # for item in payment_methods:
                #     if item['option'] == reqs_type:
                #         payment_method = item['option']
                #         bank = item['method']
                #         break

                # if payment_method is None:
                #     payment_method = payment_methods[0]['option']
                #     bank = payment_methods[0]['method']

                # response = requests.post(
                #     self.base_url + f'/api/merchant/invoices/{tr_id}/start-deal',
                #     headers=headers,
                #     json={'paymentMethod': bank, 'paymentOption': payment_method}
                # )
                # reqs = response.json()['deals'][0]['requisites']['requisites']
                # print(response.text)

                if len(response_data['deals']) != 0:
                    return {
                        'reqs': response_data['deals'][0]['requisites']['requisites'],
                        'bank': response_data['deals'][0]['paymentMethod'],
                        'label': tr_id,
                        'deal_id': response_data['deals'][0]['id']
                    }
            raise self.RequestException()
        except (
            json.decoder.JSONDecodeError,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout,
            TypeError
        ):
            raise self.RequestException()
        
    def create_dispute(self, deal_id, reason, file_path):
        with open(file_path, 'rb') as attachment:
            url = self.base_url + f'/api/merchant/invoices/{deal_id}/dispute'
            sign_string = '{0}{1}'.format('POST', url)
            signature = base64.b64encode(
                hmac.new(self.secret_key.encode(), sign_string.encode(), hashlib.sha1).digest()
            ).decode()
            response = requests.post(
                url,
                headers={
                    'X-Identity': self.api_key,
                    'X-Signature': signature,
                    'Content-Type': 'multipart/form-data'
                },
                files={
                    'attachment': attachment
                },
                data={
                    'dealId': deal_id,
                    'disputeReason': reason
                }
            )
            print(response.status_code)
            print(response.text)
