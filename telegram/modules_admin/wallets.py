from . import messages, keyboards
from wallets import BTCWallet, LTCWallet, XMRWallet, USDTWallet
from telegram.models import Transaction, Purchase, WorkingShift
import re
from general_settings.models import CryptSettings
import telebot

wallets = {
	'BTC': BTCWallet.Wallet,
	'LTC': LTCWallet.Wallet,
	'XMR': XMRWallet.Wallet,
	'USDT': USDTWallet.Wallet
}

def get_balance(bot, client):
	btc_wallet = wallets['BTC']
	btc_balance = btc_wallet.get_balance()

	ltc_wallet = wallets['LTC']
	ltc_balance = ltc_wallet.get_balance()

	xmr_wallet = wallets['XMR']
	xmr_balance = xmr_wallet.get_balance()

	usdt_wallet = wallets['USDT']
	usdt_balance = usdt_wallet.get_balance()

	context = {
		'btc_balance': btc_balance,
		'btc_rub_balance': round(btc_balance * btc_wallet.get_course()),
		'btc_address': btc_wallet.get_address(),

		'ltc_balance': ltc_balance,
		'ltc_rub_balance': round(ltc_balance * ltc_wallet.get_course()),
		'ltc_address': ltc_wallet.get_address(),

		'xmr_balance': xmr_balance,
		'xmr_rub_balance': round(xmr_balance * xmr_wallet.get_course()),
		'xmr_address': xmr_wallet.get_address(),

		'usdt_balance': usdt_balance,
		'usdt_rub_balance': round(usdt_balance * usdt_wallet.get_course()),
		'usdt_address': usdt_wallet.get_address(),
	}

	template = bot.get_template(messages.balance_message)
	mess = template.render(context)
	keyboard = keyboards.start_menu
	bot.send_message(client, mess, reply_markup=keyboard)

def send_btc(bot, client):
	crypt = 'BTC'
	client.set_state('get_address')
	client.meta['send'] = {}
	client.meta['send']['crypt'] = crypt
	client.save()

	template = bot.get_template(messages.get_address_message)
	mess = template.render(crypt=crypt)
	keyboard = keyboards.cancel_button
	bot.send_message(client, mess, reply_markup=keyboard)

def send_ltc(bot, client):
	crypt = 'LTC'
	client.set_state('get_address')
	client.meta['send'] = {}
	client.meta['send']['crypt'] = crypt
	client.save()

	template = bot.get_template(messages.get_address_message)
	mess = template.render(crypt=crypt)
	keyboard = keyboards.cancel_button
	bot.send_message(client, mess, reply_markup=keyboard)

def send_xmr(bot, client):
	crypt = 'XMR'
	client.set_state('get_address')
	client.meta['send'] = {}
	client.meta['send']['crypt'] = crypt
	client.save()

	template = bot.get_template(messages.get_address_message)
	mess = template.render(crypt=crypt)
	keyboard = keyboards.cancel_button
	bot.send_message(client, mess, reply_markup=keyboard)

def send_usdt(bot, client):
	crypt = 'USDT'
	client.set_state('get_address')
	client.meta['send'] = {}
	client.meta['send']['crypt'] = crypt
	client.save()

	template = bot.get_template(messages.get_address_message)
	mess = template.render(crypt=crypt)
	keyboard = keyboards.cancel_button
	bot.send_message(client, mess, reply_markup=keyboard)

def get_address(bot, client, message):
	if message.text == '❌ Отмена':
		client.clear_state()
		mess = messages.start_message
		keyboard = keyboards.start_menu
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	crypt = client.meta['send']['crypt']
	wallet = wallets[crypt]
	search_result = re.search(wallet.address_regex, message.text)
	if not search_result:
		template = bot.get_template(messages.incorrect_address_message)
		mess = template.render(crypt=crypt)
		keyboard = keyboards.cancel_button
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	client.set_state('get_value')
	client.meta['send']['address'] = message.text
	client.save()

	template = bot.get_template(messages.get_value_message)
	mess = template.render(crypt=crypt)
	keyboard = keyboards.cancel_button
	bot.send_message(client, mess, reply_markup=keyboard)

def get_value(bot, client, message):
	if message.text == '❌ Отмена':
		client.clear_state()
		mess = messages.start_message
		keyboard = keyboards.start_menu
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	# try:
	# 	crypt_value = float(message.text.replace(',', '.'))
	# 	if crypt_value <= 0:
	# 		raise Exception()
	# except:
		# template = bot.get_template(messages.incorrect_value_message)
		# mess = template.render(crypt=client.meta['send']['crypt'])
		# keyboard = keyboards.cancel_button
		# bot.send_message(client, mess, reply_markup=keyboard)
		# return
	search_result = re.search("(?P<value>[0-9]{1,}([,.][0-9]{1,}){0,1})", message.text)
	if not search_result:
		template = bot.get_template(messages.incorrect_value_message)
		mess = template.render(crypt=client.meta['send']['crypt'])
		keyboard = keyboards.cancel_button
		bot.send_message(client, mess, reply_markup=keyboard)
		return
		
	crypt_value = float(search_result.group("value").replace(',', '.'))
	# if client.meta['send']['crypt'] == 'XMR' and crypt_value < 0.05:
	# 	keyboard = keyboards.cancel_button
	# 	bot.send_message(client, '⛔️ Минимальная сумма: <b>0.05 XMR</b>', reply_markup=keyboard)
	# 	return

	# if client.meta['send']['crypt'] == 'BTC' and crypt_value < 0.0001:
	# 	keyboard = keyboards.cancel_button
	# 	bot.send_message(client, '⛔️ Минимальная сумма: <b>0.0001 BTC</b>', reply_markup=keyboard)
	# 	return

	# if client.meta['send']['crypt'] == 'USDT' and crypt_value < 1:
	# 	keyboard = keyboards.cancel_button
	# 	bot.send_message(client, '⛔️ Минимальная сумма: <b>1 USDT</b>', reply_markup=keyboard)
	# 	return

	client.set_state('accept_send')
	crypt = client.meta['send']['crypt']
	wallet = wallets[crypt]
	client.meta['send']['crypt_value'] = crypt_value
	client.meta['send']['rub_value'] = round(crypt_value * wallet.get_course())
	client.save()

	template = bot.get_template(messages.accept_send_message)
	mess = template.render(send=client.meta['send'])
	keyboard = keyboards.accept_send_menu
	bot.send_message(client, mess, reply_markup=keyboard)

def accept_send(bot, client, message):
	if message.text != '✅ Да':
		client.clear_state()
		mess = messages.start_message
		keyboard = keyboards.start_menu
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	client.clear_state()
	crypt = client.meta['send']['crypt']
	wallet = wallets[crypt]
	crypt_settings = CryptSettings.objects.get(name=crypt)
	if crypt_settings.auto_fee:
		fee = wallet.get_estimate_fee()
	else:
		fee = crypt_settings.fee
	result = wallet.send_crypt(client.meta['send']['address'], client.meta['send']['crypt_value'], fee)
	if type(result) != dict:
		template = bot.get_template(messages.error_send_message)
		mess = template.render(error=result)
		keyboard = keyboards.start_menu
		bot.send_message(client, mess, reply_markup=keyboard)
		return
	transaction = Transaction.objects.create(
		working_shift=WorkingShift.current(),
		crypt=crypt,
		crypt_value=client.meta['send']['crypt_value'],
		rub_value=client.meta['send']['rub_value'],
		fee=result['fee'],
		fee_rub=round(result['fee'] * wallet.get_course()),
		address=client.meta['send']['address'],
		tx_link=result['tx_link']
	)
	
	template = bot.get_template(messages.success_send_message)
	mess = template.render(transaction=transaction, total_rub=transaction.rub_value+transaction.fee_rub)
	keyboard = keyboards.start_menu
	bot.send_message(client, mess, reply_markup=keyboard)

	client.set_state('get_pay_value')
	mess = messages.get_pay_value_message
	keyboard = keyboards.ignore_button
	bot.send_message(client, mess, reply_markup=keyboard)

def start_history(bot, client):
	client.set_state('choice_history_crypt')
	client.meta['history'] = {}
	client.save()
	mess = messages.choice_crypt_message
	keyboard = keyboards.choice_crypt_menu
	bot.send_message(client, mess, reply_markup=keyboard)

def choice_history_crypt(bot, client, message):
	if message.text == 'Меню 🏠':
		client.clear_state()
		mess = messages.start_message
		keyboard = keyboards.start_menu
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	if message.text not in wallets:
		return

	client.meta['history']['crypt'] = message.text
	client.save()

	client.set_state('choice_history_type')
	mess = messages.choice_history_type_message
	keyboard = keyboards.history_menu
	bot.send_message(client, mess, reply_markup=keyboard)

def choice_history_type(bot, client, message):
	if message.text == 'Меню 🏠':
		client.clear_state()
		mess = messages.start_message
		keyboard = keyboards.start_menu
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	wallet = wallets[client.meta['history']['crypt']]
	incomig_txs, outcomig_txs = wallet.get_history()

	if message.text == 'ПРИНЯТО':
		if len(incomig_txs) == 0:
			mess = messages.empty_history_message
			keyboard = keyboards.history_menu
			bot.send_message(client, mess, reply_markup=keyboard)
			return
		template = bot.get_template(messages.history_list_message)
		mess = template.render(txs=incomig_txs[:25][::-1])
		keyboard = keyboards.history_menu
		bot.send_message(client, mess, reply_markup=keyboard)
		purchase_handler(bot, client, incomig_txs)

	elif message.text == 'ОТПРАВЛЕНО':
		if len(outcomig_txs) == 0:
			mess = messages.empty_history_message
			keyboard = keyboards.history_menu
			bot.send_message(client, mess, reply_markup=keyboard)
			return
		template = bot.get_template(messages.history_list_message)
		mess = template.render(txs=outcomig_txs[:25][::-1])
		keyboard = keyboards.history_menu
		bot.send_message(client, mess, reply_markup=keyboard)
		mess = messages.choice_history_type_message
		keyboard = keyboards.history_menu
		bot.send_message(client, mess, reply_markup=keyboard)

	else:
		return

def get_pay_value(bot, client, message):
	transaction = Transaction.objects.all().last()
	if message.text == '❌ Не учитывать':
		transaction.use_in_cashier = False
		transaction.pay_value = 0
		transaction.save()
		client.clear_state()
		mess = messages.start_message
		keyboard = keyboards.start_menu
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	try:
		pay_value = float(message.text.replace(',', '.'))
		if pay_value < 0:
			raise Exception()
	except:
		mess = messages.incorrect_pay_value_message
		bot.send_message(client, mess)
		return

	transaction.pay_value = pay_value
	transaction.save()
	transaction.report(bot)

	client.clear_state()
	mess = messages.start_message
	keyboard = keyboards.start_menu
	bot.send_message(client, mess, reply_markup=keyboard)

def purchase_handler(bot, client, incomig_txs):
	client.meta['purchase_txid'] = None
	client.save()

	for tr in incomig_txs:
		txid = tr['txid']
		if tr['crypt'] == 'BTC':
			tx_link = f"https://blockchair.com/en/bitcoin/transaction/{txid}"
		else:
			tx_link = f"https://blockchair.com/en/litecoin/transaction/{txid}"

		if Purchase.objects.filter(txid=txid, crypt=client.meta['history']['crypt']).exists():
			continue
		purchase = Purchase.objects.create(
			working_shift=WorkingShift.current(),
			txid=txid,
			crypt=tr['crypt'],
			crypt_value=tr['amount'],
			rub_value=tr['rub_amount'],
			datetime=tr['time'],
			tx_link=tx_link
		)
		client.meta['purchase_txid'] = txid
		client.save()

		client.set_state('get_purchase_pay_value')
		template = bot.get_template(messages.get_purchase_pay_value_message)
		mess = template.render(purchase=purchase)
		keyboard = keyboards.ignore_button
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	client.set_state('choice_history_type')
	mess = messages.choice_history_type_message
	keyboard = keyboards.history_menu
	bot.send_message(client, mess, reply_markup=keyboard)

def get_purchase_pay_value(bot, client, message):
	purchase = Purchase.objects.get(txid=client.meta['purchase_txid'])
	if message.text == '❌ Не учитывать':
		purchase.use_in_cashier = False
		purchase.pay_value = 0
		purchase.save()

		wallet = wallets[client.meta['history']['crypt']]
		incomig_txs, outcomig_txs = wallet.get_history()
		return purchase_handler(bot, client, incomig_txs)

	try:
		pay_value = int(message.text.replace(',', '.'))
		if pay_value < 0:
			raise Exception()
	except:
		mess = messages.incorrect_pay_value_message
		bot.send_message(client, mess)
		return

	loss = pay_value - purchase.rub_value
	percent = loss/(pay_value/100)
	if percent > 10:
		client.meta['purchase_pay_value'] = pay_value
		client.save()
		client.set_state('confirm_purchase_pay_value')
		mess = messages.confirm_purchase_pay_value_message
		keyboard = keyboards.accept_send_menu
		bot.send_message(client, mess, reply_markup=keyboard)
		return


	purchase.pay_value = pay_value
	purchase.save()
	purchase.report(bot)

	template = bot.get_template(messages.got_purchase_pay_value_message)
	mess = template.render(purchase=purchase)
	bot.send_message(client, mess)
	
	wallet = wallets[client.meta['history']['crypt']]
	incomig_txs, outcomig_txs = wallet.get_history()
	purchase_handler(bot, client, incomig_txs)

def confirm_purchase_pay_value(bot, client, message):
	purchase = Purchase.objects.get(txid=client.meta['purchase_txid'])
	pay_value = client.meta['purchase_pay_value']
	if message.text == '✅ Да':
		purchase.pay_value = pay_value
		purchase.save()
		purchase.report(bot)
		template = bot.get_template(messages.got_purchase_pay_value_message)
		mess = template.render(purchase=purchase)
		bot.send_message(client, mess)
		
		wallet = wallets[client.meta['history']['crypt']]
		incomig_txs, outcomig_txs = wallet.get_history()
		purchase_handler(bot, client, incomig_txs)

	elif message.text == '❌ Нет':
		client.set_state('get_purchase_pay_value')
		template = bot.get_template(messages.get_purchase_pay_value_message)
		mess = template.render(purchase=purchase)
		keyboard = keyboards.ignore_button
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	else:
		bot.delete_message(client, message.message_id)




























