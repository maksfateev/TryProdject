from . import messages, keyboards
from general_settings.models import GeneralSettings
import telebot


def start(bot, client):
	settings = GeneralSettings.objects.first()

	mess = messages.contacts_message
	keyboard = telebot.types.InlineKeyboardMarkup()
	keyboard.row(
		telebot.types.InlineKeyboardButton(text='Босс', url='t.me/'+settings.boss_contact)
	)
	keyboard.row(
		telebot.types.InlineKeyboardButton(text='Поддержка', url='t.me/'+settings.support_contact)
	)
	keyboard.row(
		telebot.types.InlineKeyboardButton(text='Отзывы', url='t.me/'+settings.reviews_contact)
	)
	keyboard.row(
		telebot.types.InlineKeyboardButton(text='Чат', url='t.me/'+settings.chat_contact)
	)
	keyboard.row(
		telebot.types.InlineKeyboardButton(text='Новости', url='t.me/'+settings.news_contact)
	)
	bot.send_message(client, mess, reply_markup=keyboard)