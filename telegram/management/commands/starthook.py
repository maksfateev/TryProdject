# -*- coding: utf-8 -*-
from telegram.handler import bot
from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
	help = 'Запуск вебхука'

	def handle(self, *args, **options):
		bot.remove_webhook()
		bot.set_webhook(
			url=settings.HOST + '/telegram/update/',
			drop_pending_updates=True,
			max_connections=50,
			secret_token=settings.WEBHOOK_TOKEN
		)