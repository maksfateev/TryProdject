import os, dotenv
from django.conf import settings

from .models import Client
from .bot import Bot
import telebot

import random, string
from captcha.image import ImageCaptcha

from functools import wraps
import logging
import traceback


bot = Bot(os.getenv('BOT_TOKEN'), 5)
logger = logging.getLogger('BOT')
fonts_dir = os.path.join(settings.BASE_DIR, 'telegram/fonts')
fonts = []

for file in os.listdir(fonts_dir):
	if '.ttf' in file:
		fonts.append(f'{fonts_dir}/' + file)


def create_captcha():
	# signs = ['+', '-']
	# expression = f'{random.randint(1, 100)} - {random.randint(1, 100)}'
	# secret = str(eval(expression))
	symbols = string.digits.replace('1', '').replace('7', '')
	secret = ''.join(random.choice(symbols) for _ in range(6))
	secret = secret.upper()

	captcha_path = f'{settings.BASE_DIR}/media/{random.randint(1, 1000)}.png'
	image = ImageCaptcha(fonts=fonts, width=280, height=90)
	data = image.generate(secret)
	image.write(secret, captcha_path)

	return secret, captcha_path

def protect(function):
	@wraps(function)
	def wrapper(message):
		if message.chat.id < 0:
			print(message.chat.id)
			return

		data = message.text.split()
		if len(data) == 2:
			client = Client.get_or_create(bot, message, start_value=data[1])
		else:
			client = Client.get_or_create(bot, message)

		try:

			if client.ban:
				logger.warning({'tg_id': message.chat.id, 'message': message.text, 'ignore': 'ban'})
				return

			if client.passed_captcha:
				return function(message, client=client)

			if client.state == 'passes_captcha':
				if message.text.lower() == client.meta['captcha']['secret'].lower():
					client.clear_state()
					client.passed_captcha = True
					client.meta = {}
					client.save()

					return function(message, client=client)

				logger.warning({'tg_id': message.chat.id, 'message': message.text, 'ignore': 'incorrect captcha'})
				return

			secret, captcha_path = create_captcha()
			client.meta['captcha'] = {'secret': secret}
			client.set_state('passes_captcha')
			client.save()

			logger.warning({'tg_id': message.chat.id, 'message': message.text, 'state': 'passes_captcha'})

			bot.send_photo(
				client, open(captcha_path, 'rb'),
				reply_markup=telebot.types.ReplyKeyboardRemove(),
				caption='Введите капчу!\n\n❗ДЛЯ КОРРЕКТНОГО ВВОДА КАПЧИ ОТКРОЙТЕ ИЗОБРАЖЕНИЕ ❗\n<code>Бот не будет реагировать на сообщения до корректного ввода</code>'
				)
			os.remove(captcha_path)
			return

		except Exception as e:
			logger.error({'tg_id': message.chat.id, 'message': message.text, 'state': client.state, 'error': traceback.format_exc()})

	return wrapper


















