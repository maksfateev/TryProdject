# -*- coding: utf-8 -*-
from telegram.handler import bot
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Выход бота'

    def handle(self, *args, **options):
        bot.log_out()