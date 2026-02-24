# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from django.db import transaction, close_old_connections
from django.db.models import Q

import time
from datetime import timedelta, datetime

import traceback
import logging

from telegram.models import OrderSell, Client
from telegram.handler import bot as main_bot, sell_bot

from general_settings.models import GeneralSettings
from wallets import BTCWallet, LTCWallet, XMRWallet, USDTWallet
from decimal import Decimal, getcontext

logger = logging.getLogger('PROCESS_SELL_ORDERS')
wallets = {
    'BTC': BTCWallet.Wallet,
    'LTC': LTCWallet.Wallet,
    'XMR': XMRWallet.Wallet,
    'USDT': USDTWallet.Wallet
}


class Command(BaseCommand):
    help = 'Обработка заявок на покупку'
    epsilon = Decimal('0.0')

    def handle(self, *args, **options):
        getcontext().prec = 8

        while True:
            close_old_connections()
            settings = GeneralSettings.objects.first()

            try:
                orders = OrderSell.objects.filter(Q(status='pending') | Q(status='paid') | Q(status='partially'))
                for order in orders:
                    self.process_order(order, settings)
                    time.sleep(2)
                time.sleep(5)
            except Exception as e:
                logger.error(f'Error in processing sell orders loop: {traceback.format_exc()}')
                time.sleep(5)

    def process_order(self, order, settings):
        """ Business logic of  order sell func. """
        try:
            with transaction.atomic():
                if order.status == 'partially':
                    if self.check_system_transaction(order):
                        self.recalculation_order(order)
                        return

                elif order.status == 'paid':
                    if self.check_system_transaction(order):
                        self.confirm_order(order)
                        return
                elif order.status == 'network_error':
                    return
                else:
                    if (order.datetime + timedelta(minutes=settings.time_for_sell)) < datetime.now():
                        self.reject_order(order, timeout=True)
                        return

                    self.check_wallet_transactions(order)
        except Exception as e:
            logger.error(f'Error processing order {order.order_id}: {traceback.format_exc()}')

    def confirm_order(self, order):
        """ Confirm order sell func. """
        try:
            admin_bot = self.get_admin_bot(order)
            order.confirm(main_bot, admin_bot)
            logger.info(f'Confirmed sell order {order.order_id}')
        except Exception as e:
            logger.error(f'Error confirming sell order {order.order_id}: {traceback.format_exc()}')

    def reject_order(self, order, timeout=False):
        """ Chancel order sell func. """
        try:
            order.reject(main_bot, timeout=timeout)
            logger.info(f'Rejected sell order {order.order_id}')
        except Exception as e:
            logger.error(f'Error rejecting sell order {order.order_id}: {traceback.format_exc()}')

    def recalculation_order(self, order):
        """ Recalculation data order sell func. """
        try:
            admin_bot = self.get_admin_bot(order)
            order.recalculation(main_bot, admin_bot)
            logger.info(f'Confirmed sell order, but recalculate data {order.order_id}')
        except Exception as e:
            logger.error(f'Error recalculation sell order {order.order_id}: {traceback.format_exc()}')

    def check_wallet_transactions(self, order):
        """ Check confirm transaction wallet status. """
        admin_bot = self.get_admin_bot(order)
        wallet = wallets.get(order.crypt, None)
        if wallet is None:
            return

        incoming_txs = wallet.get_receive_history()
        for receive_item in incoming_txs:
            if order.address == receive_item['address']:
                order.transaction_id = receive_item['id']
                order.save()

                user_crypt_value = order.crypt_value
                send_value = receive_item['amount']

                diff_value = Decimal(str(user_crypt_value)) - Decimal(str(send_value))

                order.set_diff_value(diff_value)

                if diff_value == self.epsilon:
                    order.set_status('paid', admin_bot)
                else:
                    admin_bot = self.get_admin_bot(order)
                    wallet = wallets.get(order.crypt, None)

                    if wallet is None:
                        return

                    amount = wallet.get_transaction_amount(order.transaction_id)
                    order.set_status('partially', admin_bot, amount)

    def check_system_transaction(self, order) -> bool:
        """ Check confirm transaction system status. """
        wallet = wallets.get(order.crypt, None)
        admin_bot = self.get_admin_bot(order)
        if wallet is None:
            return False

        transaction = wallet.get_transaction(order.transaction_id)
        if transaction['status'] == 'network_error':
            order.set_status('network_error', admin_bot)
        
        confirmations = transaction['confirmations']
        if confirmations > 0:
            return True
        return False

    def get_admin_bot(self, order):
        return sell_bot
        # match order.crypt:
        #     case 'BTC':
        #         admin_bot = btc_bot

        #     case 'LTC':
        #         admin_bot = ltc_bot

        #     case 'XMR':
        #         admin_bot = xmr_bot

        #     case 'USDT':
        #         admin_bot = usdt_bot

        # return admin_bot
