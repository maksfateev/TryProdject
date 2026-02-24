from . import messages, keyboards
from wallets import BTCWallet, LTCWallet, XMRWallet, USDTWallet
from general_settings.models import CryptSettings
import re

wallets = {
	'BTC': BTCWallet.Wallet,
	'LTC': LTCWallet.Wallet,
	'XMR': XMRWallet.Wallet,
	'USDT': USDTWallet.Wallet
}


def start(bot, client):
	client.set_state('choice_calc_crypt')
	client.meta['calculate'] = {}
	client.save()
	mess = messages.choice_crypt_message
	keyboard = keyboards.choice_crypt_menu
	bot.send_message(client, mess, reply_markup=keyboard)

def choice_crypt(bot, client, message):
	if message.text not in wallets:
		client.clear_state()
		mess = messages.start_message
		keyboard = keyboards.start_menu
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	client.meta['calculate']['crypt'] = message.text
	client.save()

	client.set_state('get_calc_percent')
	mess = messages.get_percent_message
	keyboard = keyboards.get_percent_menu
	bot.send_message(client, mess, reply_markup=keyboard)

def get_percent(bot, client, message):
	if message.text == 'Меню 🏠':
		client.clear_state()
		mess = messages.start_message
		keyboard = keyboards.start_menu
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	if message.text == 'RUB':
		client.meta['calculate']['percent'] = 'RUB'
		client.save()

		client.set_state('get_calc_value')
		template = bot.get_template(messages.get_calc_rub_value_message)
		mess = template.render(calculate=client.meta['calculate'])
		keyboard = keyboards.menu_button
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	elif '%' in message.text:
		percent = int(message.text.replace('%', ''))
		client.meta['calculate']['percent'] = percent
		client.save()

		client.set_state('get_calc_value')
		template = bot.get_template(messages.get_calc_value_message)
		mess = template.render(calculate=client.meta['calculate'])
		keyboard = keyboards.menu_button
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	else:
		return

def get_value(bot, client, message):
	if message.text == 'Меню 🏠':
		client.clear_state()
		mess = messages.start_message
		keyboard = keyboards.start_menu
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	# try:
	# 	value = float(message.text.replace(',', '.'))
	# 	if value <= 0:
	# 		raise Exception()
	# except:
		# mess = messages.incorrect_calc_value_message
		# keyboard = keyboards.menu_button
		# bot.send_message(client, mess, reply_markup=keyboard)
		# return

	search_result = re.search("(?P<value>[0-9]{1,}([,.][0-9]{1,}){0,1})", message.text)
	if not search_result:
		mess = messages.incorrect_calc_value_message
		keyboard = keyboards.menu_button
		bot.send_message(client, mess, reply_markup=keyboard)
		return
		
	value = float(search_result.group("value").replace(',', '.'))

	wallet = wallets[client.meta['calculate']['crypt']]

	if client.meta['calculate']['percent'] == 'RUB':
		result = value / wallet.get_course()
		result = "{:.8f}".format(result).rstrip('0')

		client.clear_state()
		template = bot.get_template(messages.result_rub_message)
		mess = template.render(calculate=client.meta['calculate'], result=result, value=value)
		keyboard = keyboards.start_menu
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	course = wallet.get_course()
	percent = client.meta['calculate']['percent']
	real_value = round(float(value) * course)
	comission = real_value * (percent/100)

	crypt_settings = CryptSettings.objects.get(name=client.meta['calculate']['crypt'])
	comission += crypt_settings.get_comission()

	result = round(real_value + comission)

	client.clear_state()
	template = bot.get_template(messages.result_message)
	mess = template.render(result=result, percent=percent, real_value=real_value)
	keyboard = keyboards.start_menu
	bot.send_message(client, mess, reply_markup=keyboard)












