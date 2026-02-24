import json
import requests

import logging
import datetime

from django.core.cache import cache

import os
from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger('WALLETS')


class Wallet:
	currency = 'BTC'
	network = 'bitcoin'
	address_regex = '^([13][a-km-zA-HJ-NP-Z1-9]{25,34})|^(bc1([qpzry9x8gf2tvdw0s3jn54khce6mua7l]{39}|[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{59}))$'

	API_KEY = os.environ['KAAWALLET_KEY']
	headers = {'Authorization': f'Bearer {API_KEY}'}
	base_url = 'https://kaawallet.io/api/v1'

	@classmethod
	def get_course(cls):
		course = cache.get(cls.currency)
		if not course:
			try:
				headers = {
					'X-API-Key': os.environ['CRYPTOAPIS_KEY']
				}
				url = f'https://rest.cryptoapis.io/market-data/exchange-rates/by-symbols/{cls.currency}/rub'
				response = requests.get(url, headers=headers, timeout=10)
				course = float(response.json()['data']['item']['rate'])
				print('cryptoapis')

			except:
				from general_settings.models import GeneralSettings
				settings = GeneralSettings.objects.first()
				keys = []
				for i in range(1, 5):
					if getattr(settings, f'cmc_api_key{i}') is not None:
						keys.append(getattr(settings, f'cmc_api_key{i}'))

				course = None

				for key in keys:
					try:
						url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
						params = {'convert': 'RUB', 'symbol': cls.currency}
						headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': key}
						r = requests.get(url, headers=headers, params=params)
						data = r.json()
						course = data['data'][cls.currency]['quote']['RUB']['price']

						print('coinmarketcap')
						break
					except Exception as e:
						print(e)
						continue

				if course is None:
					data = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={cls.currency}&tsyms=RUB')
					course = float(data.json().get('RUB'))

			cache.set(cls.currency, course, 120)

		return course

	@classmethod
	def get_balance(cls):
		url = cls.base_url + '/balance/'
		data = {'network': cls.network}
		response = requests.post(url, headers=cls.headers, json=data)

		balance = float(response.json()['balance'])
		logger.info({'crypt': cls.currency, 'method': 'get_balance', 'result': balance})

		return balance

	@classmethod
	def get_address(cls):
		url = cls.base_url + '/address/'
		data = {'network': cls.network}
		response = requests.post(url, headers=cls.headers, json=data)

		address = response.json()['address']
		logger.info({'crypt': cls.currency, 'method': 'get_address', 'result': address})

		return address

	@classmethod
	def get_comission(cls):
		url = cls.base_url + '/comission/'
		data = {'network': cls.network}
		response = requests.post(url, headers=cls.headers, json=data)

		comission = float(response.json()['comission'])

		return comission

	@classmethod
	def get_transaction(cls, tx_id):
		url = cls.base_url + '/transaction/'
		data = {'id': int(tx_id)}
		response = requests.post(url, headers=cls.headers, json=data)

		status = response.json()['transaction']['status']
		confirmations = 1 if status == 'confirmed' else 0

		return {'confirmations': confirmations}

	@classmethod
	def get_estimate_fee(cls):
		return 0

	@classmethod
	def send_crypt(cls, address, value, fee):
		url = cls.base_url + '/withdrawal/'
		data = {'network': cls.network, 'amount': value, 'address': address}
		response = requests.post(url, headers=cls.headers, json=data)

		if response.status_code != 200:
			try:
				errors = response.json()['errors']

				return list(errors.values())[0]

			except Exception:
				return response.text

		tr = response.json()['transaction']
		result = {
			'amount': value,
			'crypt': cls.currency,
			'address': address,
			'txid': str(tr['id']),
			'tx_link': tr['explorer_link'],
			'fee': float(tr['comission'])
		}
		logger.info({'crypt': cls.currency, 'method': 'send_crypt', 'params': [address, value], 'result': result['txid']})

		return result

	@classmethod
	def get_history(cls):
		url = cls.base_url + '/transactions/'
		data = {'network': cls.network, 'limit': 50}
		response = requests.post(url, headers=cls.headers, json=data)

		history = response.json()['transactions']
		incomig_txs = []
		outcomig_txs = []

		course = cls.get_course()

		for tr in history:
			history_item = {
				'address': tr['address'],
				'amount': float(tr['amount']),
				'time': datetime.datetime.fromtimestamp(tr['created_at']),
				'crypt': cls.currency,
				'rub_amount': round(float(tr['amount']) * course),
				'txid': str(tr['id'])
			}

			if tr['category'] == 'receive':
				incomig_txs.append(history_item)

			else:
				outcomig_txs.append(history_item)

		return incomig_txs, outcomig_txs

	@classmethod
	def get_transaction_amount(cls, tx_id):
		url = cls.base_url + '/transaction/'
		data = {'id': int(tx_id)}
		response = requests.post(url, headers=cls.headers, json=data)

		amount = response.json()['transaction']['amount']

		return amount

	@classmethod
	def get_receive_history(cls):
		url = cls.base_url + '/transactions/'
		data = {
			'network': cls.network,
			'category': 'receive',
			'limit': 50
		}
		response = requests.post(url, headers=cls.headers, json=data)

		history = response.json()['transactions']
		incomig_txs = []

		course = cls.get_course()

		for tr in history:
			history_item = {
				'id': tr['id'],
				'address': tr['address'],
				'amount': float(tr['amount']),
				'time': datetime.datetime.fromtimestamp(tr['created_at']),
				'crypt': cls.currency,
				'status': tr['status'],
				'rub_amount': round(float(tr['amount']) * course),
				'txid': str(tr['id'])
			}

			if history_item:
				incomig_txs.append(history_item)

		return incomig_txs
