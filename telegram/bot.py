import telebot
from telebot import apihelper

from jinja2 import Template
from general_settings.models import Cashier, GeneralSettings

from requests.exceptions import ConnectionError
from telebot.apihelper import ApiTelegramException

import time
from django.core.cache import cache

parse_mode = 'HTML'

# apihelper.API_URL = 'http://95.163.237.251:8081/bot{0}/{1}'
# apihelper.FILE_URL = 'http://95.163.237.251:8081'

class Bot(telebot.TeleBot):
	def __init__(self, token, num_threads):
		super().__init__(token, threaded=True, num_threads=num_threads)

	def get_me(self):
		try:
			return super().get_me()
		except ConnectionError:
			time.sleep(1)
			return super().get_me()

	def send_report(self, message):
		cashier = Cashier.objects.first()
		return super().send_message(cashier.channel, message, parse_mode=parse_mode)

	def send_profit_report(self, message):
		cashier = Cashier.objects.first()

		if cashier.profit_channel is not None:
			return super().send_message(cashier.profit_channel, message, parse_mode=parse_mode)

	def send_oper_report(self, operator, message):
		try:
			return super().send_message(operator.channel_tg_id, message, parse_mode=parse_mode)

		except Exception as e:
			print(e)

	def send_to_chat(self, message, image=None):
		tg_id = GeneralSettings.objects.first().chat_tg_id

		if image is None:
			return super().send_message(tg_id, message, parse_mode=parse_mode)
		else:
			return super().send_photo(tg_id, image, caption=message, parse_mode=parse_mode)

	def send_message(self, client, message, reply_markup=None, reply_to_message_id=None):
		tg_id = client.tg_id
		try:
			return super().send_message(tg_id, message, reply_markup=reply_markup, parse_mode=parse_mode, disable_web_page_preview=True, reply_to_message_id=reply_to_message_id)
		except:
			time.sleep(1.5)
			return super().send_message(tg_id, message, reply_markup=reply_markup, parse_mode=parse_mode, disable_web_page_preview=True, reply_to_message_id=reply_to_message_id)

	def delete_message(self, client, message_id):
		tg_id = client.tg_id
		try:
			return super().delete_message(tg_id, message_id)
		except ConnectionError:
			time.sleep(1.5)
			return super().delete_message(tg_id, message_id)
		except:
			return

	def edit_message_text(self, client, message_id, text, reply_markup=None):
		tg_id = client.tg_id
		try:
			return super().edit_message_text(chat_id=tg_id, message_id=message_id, text=text, reply_markup=reply_markup, disable_web_page_preview=True, parse_mode=parse_mode)
		except:
			time.sleep(1.5)
			return super().edit_message_text(chat_id=tg_id, message_id=message_id, text=text, reply_markup=reply_markup, disable_web_page_preview=True, parse_mode=parse_mode)

	def edit_message_caption(self, client, message_id, caption, reply_markup=None):
		tg_id = client.tg_id
		try:
			return super().edit_message_caption(chat_id=tg_id, message_id=message_id, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
		except:
			time.sleep(1.5)
			return super().edit_message_caption(chat_id=tg_id, message_id=message_id, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)

	def edit_message_media(self, client, message_id, media):
		tg_id = client.tg_id
		try:
			return super().edit_message_media(message_id=message_id, chat_id=tg_id, media=media)
		except:
			time.sleep(1.5)
			return super().edit_message_media(message_id=message_id, chat_id=tg_id, media=media)

	def send_photo(self, client, image, caption=None, reply_markup=None):
		tg_id = client.tg_id
		try:
			return super().send_photo(tg_id, image, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
		except:
			time.sleep(1.5)
			return super().send_photo(tg_id, image, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)

	def edit_message_reply_markup(self, client, message_id, reply_markup):
		tg_id = client.tg_id
		try:
			return super().edit_message_reply_markup(chat_id=tg_id, message_id=message_id, reply_markup=reply_markup)
		except:
			time.sleep(1.5)
			return super().edit_message_reply_markup(chat_id=tg_id, message_id=message_id, reply_markup=reply_markup)

	def send_dice(self, client, reply_markup=None):
		tg_id = client.tg_id
		return super().send_dice(tg_id, emoji='🎰', reply_markup=reply_markup)
	
	def send_review(self, from_chat_id, message_id):
		print("HELLLO REVIEWS")
		tg_id = GeneralSettings.objects.first().reviews_tg_id
		return super().forward_message(tg_id, from_chat_id, message_id)

	def get_template(self, message):
		return Template(message)








