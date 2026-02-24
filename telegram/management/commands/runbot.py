# -*- coding: utf-8 -*-
from telegram.handler import bot, trading_bot, btc_bot, ltc_bot, xmr_bot, usdt_bot, sell_bot
from django.core.management.base import BaseCommand

from threading import Thread

class Command(BaseCommand):
    help = 'Запуск бота'

    def handle(self, *args, **options):
        btc_bot.remove_webhook()
        thread_btc = Thread(
            target=btc_bot.infinity_polling,
            kwargs={'timeout': 10, 'long_polling_timeout': 5, 'skip_pending': True}
        )
        thread_btc.start()

        ltc_bot.remove_webhook()
        thread_ltc = Thread(
            target=ltc_bot.infinity_polling,
            kwargs={'timeout': 10, 'long_polling_timeout': 5, 'skip_pending': True}
        )
        thread_ltc.start()

        xmr_bot.remove_webhook()
        thread_xmr = Thread(
            target=xmr_bot.infinity_polling,
            kwargs={'timeout': 10, 'long_polling_timeout': 5, 'skip_pending': True}
        )
        thread_xmr.start()

        usdt_bot.remove_webhook()
        thread_usdt = Thread(
            target=usdt_bot.infinity_polling,
            kwargs={'timeout': 10, 'long_polling_timeout': 5, 'skip_pending': True}
        )
        thread_usdt.start()
        
        sell_bot.remove_webhook()
        thread_sell = Thread(
            target=sell_bot.infinity_polling,
            kwargs={'timeout': 10, 'long_polling_timeout': 5, 'skip_pending': True}
        )
        thread_sell.start()
        
        trading_bot.remove_webhook()
        thread_trading = Thread(
            target=trading_bot.infinity_polling,
            kwargs={'timeout': 10, 'long_polling_timeout': 5, 'skip_pending': True}
        )
        thread_trading.start()

        bot.remove_webhook()
        bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)