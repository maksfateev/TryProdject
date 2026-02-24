from . import messages, keyboards
from telegram.models import Client
from general_settings.models import GeneralSettings

def start(bot, client):
	mess = messages.choice_action_message
	keyboard = keyboards.ban_menu
	bot.send_message(client, mess, reply_markup=keyboard)

def start_ban(bot, client):
	client.set_state('get_ban_id')
	mess = messages.get_ban_id_message
	keyboard = keyboards.cancel_button
	bot.send_message(client, mess, reply_markup=keyboard)

def get_ban_id(bot, client, message):
	if message.text == '❌ Отмена':
		client.clear_state()
		mess = messages.start_message
		keyboard = keyboards.functional_menu
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	try:
		tg_id = int(message.text)
		if tg_id == GeneralSettings.objects.first().admin_tg_id:
			raise Exception()
		ban_client = Client.objects.get(tg_id=tg_id)
		ban_client.ban = True
		ban_client.save()
	except:
		mess = messages.incorrect_id_message
		keyboard = keyboards.cancel_button
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	client.clear_state()
	template = bot.get_template(messages.user_banned_message)
	mess = template.render(tg_id=tg_id)
	keyboard = keyboards.ban_menu
	bot.send_message(client, mess, reply_markup=keyboard)

def start_unban(bot, client):
	client.set_state('get_unban_id')
	mess = messages.get_unban_id_message
	keyboard = keyboards.cancel_button
	bot.send_message(client, mess, reply_markup=keyboard)

def get_unban_id(bot, client, message):
	if message.text == '❌ Отмена':
		client.clear_state()
		mess = messages.start_message
		keyboard = keyboards.functional_menu
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	try:
		tg_id = int(message.text)
		ban_client = Client.objects.get(tg_id=tg_id)
		ban_client.ban = False
		ban_client.save()
	except:
		mess = messages.incorrect_id_message
		keyboard = keyboards.cancel_button
		bot.send_message(client, mess, reply_markup=keyboard)
		return

	client.clear_state()
	template = bot.get_template(messages.user_unbanned_message)
	mess = template.render(tg_id=tg_id)
	keyboard = keyboards.ban_menu
	bot.send_message(client, mess, reply_markup=keyboard)








