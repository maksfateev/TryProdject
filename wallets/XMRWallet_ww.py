import requests
import json
import os
import hashlib
import hmac
from dotenv import load_dotenv
import datetime
from django.core.cache import cache
import logging
import time
from westwallet_api import WestWalletAPI
from westwallet_api.exceptions import InsufficientFundsException, BadAddressException

load_dotenv()
logger = logging.getLogger('WALLETS')

public_key = os.environ['PUBLIC_WESTWALLET']
private_key = os.environ['PRIVATE_WESTWALLET']
base_url = 'https://api.westwallet.io/wallet'
client = WestWalletAPI(public_key, private_key)
LOCAL = bool(int(os.environ['LOCAL']))


class Wallet:
	currency = 'XMR'
	network = 'monero'
	address_regex = '^(4|8)?[0-9A-Z]{1}[0-9a-zA-Z]{93}([0-9a-zA-Z]{11})?$'

	@staticmethod
	def get_course():
		course = cache.get(Wallet.currency)
		if not course:

			try:
				headers = {
					'X-API-Key': os.environ['CRYPTOAPIS_KEY'],
					'Content-Type': 'application/json'
				}
				url = f'https://rest.cryptoapis.io/market-data/exchange-rates/by-symbols/{Wallet.currency}/rub'
				response = requests.get(url, headers=headers, timeout=10)
				course = float(response.json()['data']['item']['rate'])
				print('cryptoapis')

			except Exception as e:
				print(e)
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
						params = {'convert': 'RUB', 'symbol': Wallet.currency}
						headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': key}
						r = requests.get(url, headers=headers, params=params)
						data = r.json()
						course = data['data'][Wallet.currency]['quote']['RUB']['price']

						print('coinmarketcap')
						break
					except Exception as e:
						print(e)
						continue

				if course is None:
					data = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={Wallet.currency}&tsyms=RUB')
					course = float(data.json().get('RUB'))

			cache.set(Wallet.currency, course, 120)

		return course

	@staticmethod
	def get_balance():
		try:
			balance = client.wallet_balance(Wallet.currency)
			logger.info({'crypt': Wallet.currency, 'method': 'get_balance', 'result': balance})
			return float(balance.balance)
		except Exception as e:
			print(e)
			return 0.0

	@staticmethod
	def get_address():
		try:
			address = client.generate_address(Wallet.currency, 'https://artbossbot.ru/callback')
			logger.info({'crypt': Wallet.currency, 'method': 'get_address', 'result': address})
			return address.address
		except Exception as e:
			print(e)
			return '-'

	@staticmethod
	def get_transaction(tx_id):
		transaction = client.transaction_info(tx_id)
		return transaction.__dict__['blockchain_hash']

	@staticmethod
	def get_estimate_fee():
		return 13

	@staticmethod
	def send_crypt(address, value, fee):
		if LOCAL:
			logger.info({'crypt': Wallet.currency, 'method': 'send_crypt', 'params': [address, value], 'result': 'fefdfdfdfdfd'})
			return {
				'amount': value,
				'crypt': Wallet.currency,
				'address': address,
				'txid': 'fefdfdfdfdfd',
				'tx_link': f"https://blockchair.com/en/{Wallet.network}/transaction/fefdfdfdfdfd",
				'fee': 0.00001
			}
			
		try:
			transaction = client.create_withdrawal(Wallet.currency, str(value), address)
		except InsufficientFundsException:
			return 'Недостаточно XMR для отправки'
		except BadAddressException:
			return 'Некорректный XMR адрес'

		result = {
			'amount': value,
			'crypt': Wallet.currency,
			'address': address,
			'txid': str(transaction.__dict__['id']),
			'tx_link': 'https://xmr-explorer.ru/transaction/menyala/' + str(transaction.__dict__['id']),
			'fee': float(transaction.__dict__['fee'])
		}
		logger.info({'crypt': Wallet.currency, 'method': 'send_crypt', 'params': [address, value], 'result': result['txid']})
		return result

	@staticmethod
	def get_history():
		try:
			history = cache.get('westwallet-history')

			if history is None:
				data = {'limit': 100}
				timestamp = int(time.time())
				dumped = json.dumps(data, ensure_ascii=False)
				sign = hmac.new(private_key.encode('utf-8'), "{}{}".format(timestamp, dumped).encode('utf-8'), hashlib.sha256).hexdigest()
				headers = {
					"Content-Type": "application/json",
					"X-API-KEY": public_key,
					"X-ACCESS-SIGN": sign,
					"X-ACCESS-TIMESTAMP": str(timestamp)
				}
				resp = requests.post("https://api.westwallet.io/wallet/transactions", data=json.dumps(data), headers=headers)
				if resp.status_code != 200:
					time.sleep(2)
					resp = requests.post("https://api.westwallet.io/wallet/transactions", data=json.dumps(data), headers=headers)
					
				history = resp.json()['result']
				cache.set('westwallet-history', history, 60)

			incomig_txs = []
			outcomig_txs = []
			for tr in history:
				if tr['currency'] == Wallet.currency:
					history_item = {
						# 'address': tr['to_address'],
						'amount': tr['amount'],
						'time': datetime.datetime.strptime(tr['created_at'], '%Y-%m-%d %H:%M:%S'),
						'crypt': Wallet.currency,
						'rub_amount': round(float(tr['amount']) * Wallet.get_course()),
						'txid': tr['blockchain_hash']
					}

					if tr['type'] == 'send':
						history_item['address'] = tr['to_address']
						outcomig_txs.append(history_item)
					else:
						if not history_item['txid']:
							history_item['txid'] = str(tr['id'])
						history_item['address'] = tr['address']
						incomig_txs.append(history_item)

			return incomig_txs, outcomig_txs

		except Exception as e:
			print(e)
			return [], []





















