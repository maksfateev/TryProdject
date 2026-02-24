# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from django.db import transaction, close_old_connections
from django.db.models import Q

import time
from datetime import timedelta, datetime

import traceback
import logging

import telebot

from telegram.models import Order, Client
from telegram.handler import btc_bot, ltc_bot, xmr_bot, usdt_bot
from telegram.handler import bot as main_bot
from telegram.modules_admin import messages
from django.core.cache import cache
from general_settings.models import GeneralSettings

logger = logging.getLogger('PROCESS_ORDERS')

class Command(BaseCommand):
    help = 'Обработка заявок'

    def handle(self, *args, **options):
        while True:
            close_old_connections()
            settings = GeneralSettings.objects.first()
            orders = Order.objects.filter(status='pending')
            ids = [order.id for order in orders]
            # for order in orders:
            for id in ids:
                order = Order.objects.get(id=id)
                if order.status != 'pending':
                    continue

                match order.crypt:
                    case 'BTC':
                        bot = btc_bot

                    case 'LTC':
                        bot = ltc_bot

                    case 'XMR':
                        bot = xmr_bot

                    case 'USDT':
                        bot = usdt_bot
                    
                if order.notification and settings.auto_handler and order.message_id is not None:
                    try:
                        order.confirm(main_bot, bot)
                        logger.info(f'Confirm order {order.order_id}')
                    except Exception as e:
                        logger.error(f'Error with confirm order {order.order_id}: {traceback.format_exc()}')
                    continue

                if (order.datetime + timedelta(minutes=settings.time_for_order)) < datetime.now():
                    if order.message_id is None:
                        order.status = 'timeouted'
                        order.save()
                    else:
                        try:
                            order.reject(main_bot, bot, timeout=True)
                            logger.info(f'Reject order {order.order_id}')
                        except Exception as e:
                            logger.error(f'Error with reject order {order.order_id}: {traceback.format_exc()}')
                    continue
                    
                with transaction.atomic():
                    order = Order.objects.select_for_update().get(id=order.id)
                    order.search_notification()
                    
                    if order.status == 'pending':
                        admin = Client.objects.get(tg_id=settings.admin_tg_id)
                        template = main_bot.get_template(messages.order_message)
                        mess = template.render(order=order, auto_handler=settings.auto_handler)
                        keyboard = None
                        has_keyboard = False
                        
                        if not settings.auto_handler:
                            keyboard = telebot.types.InlineKeyboardMarkup()
                            keyboard.row(
                                telebot.types.InlineKeyboardButton(text='✅ Подтвердить', callback_data=f'confirm_order-{order.id}'),
                                telebot.types.InlineKeyboardButton(text='❌ Отклонить', callback_data=f'reject_order-{order.id}'),
                            )
                            has_keyboard = True
                        
                        order_cache = cache.get(f'order_{order.id}') or {'message': None, 'has_keyboard': False}

                        if order_cache['message'] != mess or order_cache['has_keyboard'] != has_keyboard:
                            try:
                                bot.edit_message_text(admin, order.message_id, mess, reply_markup=keyboard)

                            except:
                                logger.error({'order_update_id': order.order_id, 'error': traceback.format_exc()})

                        cache.set(
                            f'order_{order.id}',
                            {'message': mess, 'has_keyboard': has_keyboard},
                            settings.time_for_order * 60
                        )
                        # try:
                        # 	bot.edit_message_text(admin, order.message_id, mess, reply_markup=keyboard)
                        # except Exception as e:
                        # 	pass

                time.sleep(2)

            time.sleep(5)

