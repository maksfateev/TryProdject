from . import messages, keyboards
from general_settings.models import CryptSettings, GeneralSettings, CryptSellSettings
from wallets import BTCWallet, LTCWallet, XMRWallet, USDTWallet
import telebot
wallets = {
	'BTC': BTCWallet.Wallet,
	'LTC': LTCWallet.Wallet,
	'XMR': XMRWallet.Wallet,
	'USDT': USDTWallet.Wallet
}

def start(bot, client):
	mess = messages.start_settings_message
	keyboard = keyboards.settings_menu
	bot.send_message(client, mess, reply_markup=keyboard)

def start_settings(bot, client, call):
	data = call.data.split('-')
	crypt = data[1].upper()

	if crypt == 'AUTO':
		settings = GeneralSettings.objects.first()
		template = bot.get_template(messages.settings_auto_message)
		mess = template.render(auto_handler=settings.auto_handler)
		keyboard = telebot.types.InlineKeyboardMarkup()
		keyboard.row(
			telebot.types.InlineKeyboardButton(text='✅ВКЛ', callback_data=f'settings_on-auto'),
			telebot.types.InlineKeyboardButton(text='❌ВЫКЛ', callback_data=f'settings_off-auto'),
		)
		bot.edit_message_text(client, call.message.message_id, mess, reply_markup=keyboard)
		return

	if crypt == 'XMR':
		crypt_settings = CryptSettings.objects.get(name=crypt)
		template = bot.get_template(messages.settings_xmr_message)
		mess = template.render(settings=crypt_settings)
		keyboard = telebot.types.InlineKeyboardMarkup()
		keyboard.row(
			telebot.types.InlineKeyboardButton(text='✅ВКЛ', callback_data=f'settings_on-xmr'),
			telebot.types.InlineKeyboardButton(text='❌ВЫКЛ', callback_data=f'settings_off-xmr'),
		)
		bot.edit_message_text(client, call.message.message_id, mess, reply_markup=keyboard)
		return

	if crypt == 'USDT':
		crypt_settings = CryptSettings.objects.get(name=crypt)
		template = bot.get_template(messages.settings_usdt_message)
		mess = template.render(settings=crypt_settings)
		keyboard = telebot.types.InlineKeyboardMarkup()
		keyboard.row(
			telebot.types.InlineKeyboardButton(text='✅ВКЛ', callback_data=f'settings_on-usdt'),
			telebot.types.InlineKeyboardButton(text='❌ВЫКЛ', callback_data=f'settings_off-usdt'),
		)
		bot.edit_message_text(client, call.message.message_id, mess, reply_markup=keyboard)
		return

	if crypt == 'SELL':
		crypts_sell = CryptSellSettings.objects.all()
		template = bot.get_template(messages.settings_sell_message)
		mess = template.render(on=crypts_sell.first().available)
		keyboard = telebot.types.InlineKeyboardMarkup()
		keyboard.row(
			telebot.types.InlineKeyboardButton(text='✅ВКЛ', callback_data=f'settings_on-sell'),
			telebot.types.InlineKeyboardButton(text='❌ВЫКЛ', callback_data=f'settings_off-sell'),
		)
		bot.edit_message_text(client, call.message.message_id, mess, reply_markup=keyboard)
		return


	crypt_settings = CryptSettings.objects.get(name=crypt)
	wallet = wallets[crypt]
	if crypt_settings.auto_fee:
		fee = wallet.get_estimate_fee()
	else:
		fee = crypt_settings.fee
	template = bot.get_template(messages.settings_crypt_message)
	mess = template.render(settings=crypt_settings, fee=fee)
	keyboard = telebot.types.InlineKeyboardMarkup()
	keyboard.row(
		telebot.types.InlineKeyboardButton(text='✅ВКЛ', callback_data=f'settings_on-{crypt.lower()}'),
		telebot.types.InlineKeyboardButton(text='❌ВЫКЛ', callback_data=f'settings_off-{crypt.lower()}'),
		telebot.types.InlineKeyboardButton(text='💸FEE', callback_data=f'settings_fee-{crypt.lower()}'),
	)
	bot.edit_message_text(client, call.message.message_id, mess, reply_markup=keyboard)

def settings_on(bot, client, call):
	data = call.data.split('-')
	crypt = data[1].upper()

	if crypt == 'AUTO':
		settings = GeneralSettings.objects.first()
		settings.auto_handler = True
		settings.save()
		template = bot.get_template(messages.settings_auto_message)
		mess = template.render(auto_handler=settings.auto_handler)
		keyboard = telebot.types.InlineKeyboardMarkup()
		keyboard.row(
			telebot.types.InlineKeyboardButton(text='✅ВКЛ', callback_data=f'settings_on-auto'),
			telebot.types.InlineKeyboardButton(text='❌ВЫКЛ', callback_data=f'settings_off-auto'),
		)
		bot.edit_message_text(client, call.message.message_id, mess, reply_markup=None)
		return

	if crypt == 'XMR':
		crypt_settings = CryptSettings.objects.get(name=crypt)
		crypt_settings.available = True
		crypt_settings.save()
		template = bot.get_template(messages.settings_xmr_message)
		mess = template.render(settings=crypt_settings)
		keyboard = telebot.types.InlineKeyboardMarkup()
		keyboard.row(
			telebot.types.InlineKeyboardButton(text='✅ВКЛ', callback_data=f'settings_on-{crypt.lower()}'),
			telebot.types.InlineKeyboardButton(text='❌ВЫКЛ', callback_data=f'settings_off-{crypt.lower()}'),
		)
		bot.edit_message_text(client, call.message.message_id, mess, reply_markup=None)
		return

	if crypt == 'USDT':
		crypt_settings = CryptSettings.objects.get(name=crypt)
		crypt_settings.available = True
		crypt_settings.save()
		template = bot.get_template(messages.settings_usdt_message)
		mess = template.render(settings=crypt_settings)
		keyboard = telebot.types.InlineKeyboardMarkup()
		keyboard.row(
			telebot.types.InlineKeyboardButton(text='✅ВКЛ', callback_data=f'settings_on-{crypt.lower()}'),
			telebot.types.InlineKeyboardButton(text='❌ВЫКЛ', callback_data=f'settings_off-{crypt.lower()}'),
		)
		bot.edit_message_text(client, call.message.message_id, mess, reply_markup=None)
		return

	if crypt == 'SELL':
		crypts_sell = CryptSellSettings.objects.all()
		crypts_sell.update(available=True)

		template = bot.get_template(messages.settings_sell_message)
		mess = template.render(on=crypts_sell.first().available)
		keyboard = telebot.types.InlineKeyboardMarkup()
		keyboard.row(
			telebot.types.InlineKeyboardButton(text='✅ВКЛ', callback_data=f'settings_on-sell'),
			telebot.types.InlineKeyboardButton(text='❌ВЫКЛ', callback_data=f'settings_off-sell'),
		)
		bot.edit_message_text(client, call.message.message_id, mess, reply_markup=None)
		return


	crypt_settings = CryptSettings.objects.get(name=crypt)
	crypt_settings.available = True
	crypt_settings.save()
	template = bot.get_template(messages.settings_crypt_message)
	mess = template.render(settings=crypt_settings)
	keyboard = telebot.types.InlineKeyboardMarkup()
	keyboard.row(
		telebot.types.InlineKeyboardButton(text='✅ВКЛ', callback_data=f'settings_on-{crypt.lower()}'),
		telebot.types.InlineKeyboardButton(text='❌ВЫКЛ', callback_data=f'settings_off-{crypt.lower()}'),
		telebot.types.InlineKeyboardButton(text='💸FEE', callback_data=f'settings_fee-{crypt.lower()}'),
	)
	bot.edit_message_text(client, call.message.message_id, mess, reply_markup=None)

def settings_off(bot, client, call):
	data = call.data.split('-')
	crypt = data[1].upper()

	if crypt == 'AUTO':
		settings = GeneralSettings.objects.first()
		settings.auto_handler = False
		settings.save()
		template = bot.get_template(messages.settings_auto_message)
		mess = template.render(auto_handler=settings.auto_handler)
		keyboard = telebot.types.InlineKeyboardMarkup()
		keyboard.row(
			telebot.types.InlineKeyboardButton(text='✅ВКЛ', callback_data=f'settings_on-auto'),
			telebot.types.InlineKeyboardButton(text='❌ВЫКЛ', callback_data=f'settings_off-auto'),
		)
		bot.edit_message_text(client, call.message.message_id, mess, reply_markup=None)
		return

	if crypt == 'XMR':
		crypt_settings = CryptSettings.objects.get(name=crypt)
		crypt_settings.available = False
		crypt_settings.save()
		template = bot.get_template(messages.settings_xmr_message)
		mess = template.render(settings=crypt_settings)
		keyboard = telebot.types.InlineKeyboardMarkup()
		keyboard.row(
			telebot.types.InlineKeyboardButton(text='✅ВКЛ', callback_data=f'settings_on-{crypt.lower()}'),
			telebot.types.InlineKeyboardButton(text='❌ВЫКЛ', callback_data=f'settings_off-{crypt.lower()}'),
		)
		bot.edit_message_text(client, call.message.message_id, mess, reply_markup=None)
		return

	if crypt == 'USDT':
		crypt_settings = CryptSettings.objects.get(name=crypt)
		crypt_settings.available = False
		crypt_settings.save()
		template = bot.get_template(messages.settings_usdt_message)
		mess = template.render(settings=crypt_settings)
		keyboard = telebot.types.InlineKeyboardMarkup()
		keyboard.row(
			telebot.types.InlineKeyboardButton(text='✅ВКЛ', callback_data=f'settings_on-{crypt.lower()}'),
			telebot.types.InlineKeyboardButton(text='❌ВЫКЛ', callback_data=f'settings_off-{crypt.lower()}'),
		)
		bot.edit_message_text(client, call.message.message_id, mess, reply_markup=None)
		return

	if crypt == 'SELL':
		crypts_sell = CryptSellSettings.objects.all()
		crypts_sell.update(available=False)

		template = bot.get_template(messages.settings_sell_message)
		mess = template.render(on=crypts_sell.first().available)
		keyboard = telebot.types.InlineKeyboardMarkup()
		keyboard.row(
			telebot.types.InlineKeyboardButton(text='✅ВКЛ', callback_data=f'settings_on-sell'),
			telebot.types.InlineKeyboardButton(text='❌ВЫКЛ', callback_data=f'settings_off-sell'),
		)
		bot.edit_message_text(client, call.message.message_id, mess, reply_markup=None)
		return

	crypt_settings = CryptSettings.objects.get(name=crypt)
	crypt_settings.available = False
	crypt_settings.save()
	template = bot.get_template(messages.settings_crypt_message)
	mess = template.render(settings=crypt_settings)
	keyboard = telebot.types.InlineKeyboardMarkup()
	keyboard.row(
		telebot.types.InlineKeyboardButton(text='✅ВКЛ', callback_data=f'settings_on-{crypt.lower()}'),
		telebot.types.InlineKeyboardButton(text='❌ВЫКЛ', callback_data=f'settings_off-{crypt.lower()}'),
		telebot.types.InlineKeyboardButton(text='💸FEE', callback_data=f'settings_fee-{crypt.lower()}'),
	)
	bot.edit_message_text(client, call.message.message_id, mess, reply_markup=None)

def settings_fee(bot, client, call):
	data = call.data.split('-')
	crypt = data[1].upper()
	client.meta['settings_fee'] = {}
	client.meta['settings_fee']['crypt'] = crypt
	client.save()

	client.set_state('get_fee')
	template = bot.get_template(messages.get_fee_message)
	mess = template.render(crypt=crypt)
	keyboard = keyboards.get_fee_menu
	bot.send_message(client, mess, reply_markup=keyboard)

def get_fee(bot, client, message):
	if message.text == '❌ Отмена':
		client.clear_state()
		mess = messages.start_message
		keyboard = keyboards.functional_menu
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	crypt_settings = CryptSettings.objects.get(name=client.meta['settings_fee']['crypt'])
	if message.text == '♻️ АВТО':
		crypt_settings.auto_fee = True
		crypt_settings.save()

		client.clear_state()
		template = bot.get_template(messages.set_auto_fee_message)
		mess = template.render(crypt=crypt_settings.name)
		keyboard = keyboards.functional_menu
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	try:
		fee = int(message.text)
		if fee < 10:
			raise Exception()
	except:
		mess = messages.incorrect_calc_value_message
		keyboard = keyboards.get_fee_menu
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	crypt_settings.auto_fee = False
	crypt_settings.fee = fee
	crypt_settings.save()

	client.clear_state()
	template = bot.get_template(messages.set_fee_message)
	mess = template.render(fee=fee, crypt=crypt_settings.name)
	keyboard = keyboards.functional_menu
	bot.send_message(client, mess, reply_markup=keyboard)
	






