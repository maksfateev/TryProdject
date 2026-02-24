# -*- coding: utf-8 -*-
from telegram.handler import bot
from django.core.management.base import BaseCommand

class Command(BaseCommand):
	help = 'Запуск вебхука'

	def handle(self, *args, **options):
		bot.remove_webhook()