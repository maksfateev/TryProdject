from . import messages, keyboards
from telegram.models import Order, WorkingShift, OrderSell, Client
from wallets import BTCWallet, LTCWallet
import telebot

import threading
from general_settings.models import Card, CardStats, GeneralSettings

from telegram import handler
# from bot_settings.models import Contacts, CryptSettings, BonusSettings

static_path = 'telegram/modules_admin/static/'
wallets = {'BTC': BTCWallet.Wallet, 'LTC': LTCWallet.Wallet}

def reject_order(admin_bot, client, call):
	data = call.data.split('-')
	order = Order.objects.get(id=int(data[1]))
	order.reject(handler.bot, admin_bot)

def confirm_order(admin_bot, client, call, order=None):
	data = call.data.split('-')
	order = Order.objects.get(id=int(data[1]))
	thread = threading.Thread(target=order.confirm, args=(handler.bot, admin_bot, ), name=order.order_id)
	thread.start()

	try:
		if 'card_id' in order.payload.keys():
			card = Card.objects.get(id=order.payload['card_id'])
			stats = CardStats.objects.filter(card=card, stopped_at=None).last()
			if stats:
				stats.turnover = round(stats.turnover + order.pay_value)
				stats.save()
	except:
		pass


def complete_order_sell_rec(admin_bot, client, call):
	data = call.data.split('-')
	order = OrderSell.objects.get(id=int(data[1]))
	order.status = 'completed'
	order.save()

	status = '🚀 Выполнена'
	settings = GeneralSettings.objects.first()
	admin = Client.objects.get(tg_id=settings.admin_tg_id)

	template = admin_bot.get_template(messages.order_sell_recalculate_message)
	mess = template.render(order_sell=order, status=status)

	admin_bot.edit_message_text(admin, order.message_id, mess, reply_markup=None)

	template = handler.bot.get_template(messages.completed_sell_order_message)
	mess = template.render(order_sell=order)
	handler.bot.send_message(order.client, mess)


def complete_order_sell(admin_bot, client, call):
	data = call.data.split('-')
	order = OrderSell.objects.get(id=int(data[1]))
	order.status = 'completed'
	order.save()

	status = '🚀 Выполнена'
	settings = GeneralSettings.objects.first()
	admin = Client.objects.get(tg_id=settings.admin_tg_id)

	template = admin_bot.get_template(messages.order_sell_message)
	mess = template.render(order_sell=order, status=status)

	admin_bot.edit_message_text(admin, order.message_id, mess, reply_markup=None)

	template = handler.bot.get_template(messages.completed_sell_order_message)
	mess = template.render(order_sell=order)
	handler.bot.send_message(order.client, mess)












