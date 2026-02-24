from . import messages, keyboards
from general_settings.models import PaymentMethod
import telebot
from telegram.models import Notification

def start(bot, client):
	return
	cards = PaymentMethod.objects.all()
	for card in cards:
		template = bot.get_template(messages.card_message)
		mess = template.render(card=card)
		keyboard = telebot.types.InlineKeyboardMarkup()
		keyboard.row(
			telebot.types.InlineKeyboardButton(text='💳', callback_data=f'change_requisites-card-{card.id}'),
			telebot.types.InlineKeyboardButton(text='📱', callback_data=f'change_requisites-sbp-{card.id}'),
		)
		bot.send_message(client, mess, reply_markup=keyboard)

def change_requisites(bot, client, call):
	data = call.data.split('-')
	payment_method = PaymentMethod.objects.get(id=int(data[2]))
	client.meta['change_card'] = {}
	client.meta['change_card']['id'] = int(data[2])
	client.meta['change_card']['method'] = data[1]
	client.save()

	client.set_state('get_requisites')
	template = bot.get_template(messages.change_requisites_message)
	mess = template.render(card=payment_method, method=data[1])
	keyboard = keyboards.cancel_button
	bot.send_message(client, mess, reply_markup=keyboard)

def get_requisites(bot, client, message):
	if message.text == '❌ Отмена':
		client.clear_state()
		mess = messages.start_message
		keyboard = keyboards.start_menu
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	payment_method = PaymentMethod.objects.get(id=client.meta['change_card']['id'])
	if client.meta['change_card']['method'] == 'card':
		payment_method.card_number = message.text
	else:
		payment_method.sbp_number = message.text
	payment_method.save()

	client.clear_state()
	template = bot.get_template(messages.changed_requisites_message)
	mess = template.render(card=payment_method, method=client.meta['change_card']['method'])
	keyboard = keyboards.start_menu
	bot.send_message(client, mess, reply_markup=keyboard)

def change_balance(bot, client, call):
	data = call.data.split('-')
	payment_method = PaymentMethod.objects.get(id=int(data[1]))
	client.meta['change_card'] = {}
	client.meta['change_card']['id'] = int(data[1])
	client.save()

	client.set_state('get_balance')
	template = bot.get_template(messages.change_balance_message)
	mess = template.render(card=payment_method)
	keyboard = keyboards.cancel_button
	bot.send_message(client, mess, reply_markup=keyboard)

def get_balance(bot, client, message):
	if message.text == '❌ Отмена':
		client.clear_state()
		mess = messages.start_message
		keyboard = keyboards.start_menu
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	try:
		balance = float(message.text.replace(',', '.'))
	except:
		mess = messages.incorrect_calc_value_message
		keyboard = keyboards.cancel_button
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	payment_method = PaymentMethod.objects.get(id=client.meta['change_card']['id'])
	payment_method.balance = balance
	payment_method.save()

	client.clear_state()
	template = bot.get_template(messages.changed_balance_message)
	mess = template.render(card=payment_method)
	keyboard = keyboards.start_menu
	bot.send_message(client, mess, reply_markup=keyboard)

def notification_history(bot, client):
	notifications = list(Notification.objects.all())[::-1][:10]
	template = bot.get_template(messages.notification_history_message)
	mess = template.render(notifications=notifications[::-1])
	keyboard = keyboards.start_menu
	bot.send_message(client, mess, reply_markup=keyboard)

def confirm_notification(bot, client, call):
	data = call.data.split('-')
	notification = Notification.objects.get(id=int(data[1]))
	notification.confirmed = True
	notification.save()

	payment_method = PaymentMethod.objects.get(id=1)
	payment_method.balance = notification.balance
	payment_method.save()

	bot.edit_message_text(client, call.message.message_id, f'Банк: {payment_method.name}\n✅💸 <b>Подтвержденное пополнение</b> <code>{notification.pay}</code> RUB. Баланс: <code>{notification.balance}</code> RUB')








