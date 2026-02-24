# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from stats.models import DayStats

import datetime
from telegram.models import Client, Order

import os, dotenv
dotenv.load_dotenv()
import telebot


message = '''
<b>Общая статистика</b>
----------------

Кол-во регистраций: <code>{count_register}</code>

Кол-во оплаченных заявок: <code>{payed_orders}</code>
Кол-во отмененных заявок: <code>{canceled_orders}</code>

Кол-во выданных реквизитов: <code>{issued_requisites}</code>
Соотношение заявок к суммам для оплаты: <code>{orders_about_issued_requisites}%</code>

Кол-во выданных сумм для оплаты: <code>{issued_pay_values}</code>
Соотношение заявок к суммам для оплаты: <code>{orders_about_issued_pay_values}%</code>

<b>0р - 5000р</b>
----------------

Кол-во оплаченных заявок: <code>{payed_orders_0_5000}</code>
Кол-во отмененных заявок: <code>{canceled_orders_0_5000}</code>

Кол-во выданных реквизитов: <code>{issued_requisites_0_5000}</code>
Соотношение заявок к суммам для оплаты: <code>{orders_about_issued_requisites_0_5000}%</code>

Кол-во выданных сумм для оплаты: <code>{issued_pay_values_0_5000}</code>
Соотношение заявок к суммам для оплаты: <code>{orders_about_issued_pay_values_0_5000}%</code>

<b>5000р - 10000р</b>
----------------

Кол-во оплаченных заявок: <code>{payed_orders_5000_10000}</code>
Кол-во отмененных заявок: <code>{canceled_orders_5000_10000}</code>

Кол-во выданных реквизитов: <code>{issued_requisites_5000_10000}</code>
Соотношение заявок к суммам для оплаты: <code>{orders_about_issued_requisites_5000_10000}%</code>

Кол-во выданных сумм для оплаты: <code>{issued_pay_values_0_5000}</code>
Соотношение заявок к суммам для оплаты: <code>{orders_about_issued_pay_values_5000_10000}%</code>

<b>10000 - 30000р</b>
----------------

Кол-во оплаченных заявок: <code>{payed_orders_10000_30000}</code>
Кол-во отмененных заявок: <code>{canceled_orders_10000_30000}</code>

Кол-во выданных реквизитов: <code>{issued_requisites_10000_30000}</code>
Соотношение заявок к суммам для оплаты: <code>{orders_about_issued_requisites_10000_30000}%</code>

Кол-во выданных сумм для оплаты: <code>{issued_pay_values_10000_30000}</code>
Соотношение заявок к суммам для оплаты: <code>{orders_about_issued_pay_values_10000_30000}%</code>

<b>30000 - 50000р</b>
----------------

Кол-во оплаченных заявок: <code>{payed_orders_30000_50000}</code>
Кол-во отмененных заявок: <code>{canceled_orders_30000_50000}</code>

Кол-во выданных реквизитов: <code>{issued_requisites_30000_50000}</code>
Соотношение заявок к суммам для оплаты: <code>{orders_about_issued_requisites_30000_50000}%</code>

Кол-во выданных сумм для оплаты: <code>{issued_pay_values_30000_50000}</code>
Соотношение заявок к суммам для оплаты: <code>{orders_about_issued_pay_values_30000_50000}%</code>

<b>50000р +</b>
----------------

Кол-во оплаченных заявок: <code>{payed_orders_50000_}</code>
Кол-во отмененных заявок: <code>{canceled_orders_50000_}</code>

Кол-во выданных реквизитов: <code>{issued_requisites_50000_}</code>
Соотношение заявок к суммам для оплаты: <code>{orders_about_issued_requisites_50000_}%</code>

Кол-во выданных сумм для оплаты: <code>{issued_pay_values_50000_}</code>
Соотношение заявок к суммам для оплаты: <code>{orders_about_issued_pay_values_50000_}%</code>

Группы клиентов
----------------

Пидоры: <code>{pidors_count}</code>
'''



class Command(BaseCommand):
	help = 'Выгрузка статистики'

	def _count_registers(self):
		return str(self.obj.count_registers())

	def _count_payed_orders(self, from_value=None, to_value=None):
		return str(self.obj.count_payed_orders(from_value=from_value, to_value=to_value))

	def _count_canceled_orders(self, from_value=None, to_value=None):
		return str(self.obj.count_canceled_orders(from_value=from_value, to_value=to_value))

	def _count_issued_requisites(self, from_value=None, to_value=None):
		return str(self.obj.count_issued_requisites(from_value=from_value, to_value=to_value))

	def _orders_about_issued_requisites(self, from_value=None, to_value=None):
		issued_requisites = self.obj.count_issued_requisites(from_value=from_value, to_value=to_value)
		if issued_requisites == 0:
			percent = 100
		else:
			orders = self.obj.count_payed_orders(from_value=from_value, to_value=to_value)
			percent = orders / (issued_requisites / 100)

		return f'{round(percent, 2)}%'

	def _count_issued_pay_values(self, from_value=None, to_value=None):
		return str(self.obj.count_issued_pay_values(from_value=from_value, to_value=to_value))

	def _orders_about_issued_pay_values(self, from_value=None, to_value=None):
		pay_values = self.obj.count_issued_pay_values(from_value=from_value, to_value=to_value)
		if pay_values == 0:
			percent = 100
		else:
			orders = self.obj.count_payed_orders(from_value=from_value, to_value=to_value)
			percent = orders / (pay_values / 100)

		return f'{round(percent, 2)}%'

	def _pidors_count(self):
		clients = []
		now = datetime.datetime.now()
		qs = Client.objects.filter(count__gte=5, active=True)
		for client in qs:
			orders = Order.objects.filter(client=client, status='confirmed')
			last_order = orders.last()
			if last_order and (now - last_order.datetime).days >= 20:
				clients.append(client)

		return len(clients)


	def handle(self, *args, **options):
		self.obj = DayStats.objects.first()
		channel_id = -1002105922453
		bot = telebot.TeleBot(os.environ['BOT_TOKEN'])

		mess = message.format(
			count_register=self._count_registers(),
			payed_orders=self._count_payed_orders(),
			canceled_orders=self._count_canceled_orders(),
			issued_requisites=self._count_issued_requisites(),
			orders_about_issued_requisites=self._orders_about_issued_requisites(),
			issued_pay_values=self._count_issued_pay_values(),
			orders_about_issued_pay_values=self._orders_about_issued_pay_values(),

			payed_orders_0_5000=self._count_payed_orders(from_value=0, to_value=5000),
			canceled_orders_0_5000=self._count_canceled_orders(from_value=0, to_value=5000),
			issued_requisites_0_5000=self._count_issued_requisites(from_value=0, to_value=5000),
			orders_about_issued_requisites_0_5000=self._orders_about_issued_requisites(from_value=0, to_value=5000),
			issued_pay_values_0_5000=self._count_issued_pay_values(from_value=0, to_value=5000),
			orders_about_issued_pay_values_0_5000=self._orders_about_issued_pay_values(from_value=0, to_value=5000),

			payed_orders_5000_10000=self._count_payed_orders(from_value=5000, to_value=10000),
			canceled_orders_5000_10000=self._count_canceled_orders(from_value=5000, to_value=10000),
			issued_requisites_5000_10000=self._count_issued_requisites(from_value=5000, to_value=10000),
			orders_about_issued_requisites_5000_10000=self._orders_about_issued_requisites(from_value=5000, to_value=10000),
			issued_pay_values_5000_10000=self._count_issued_pay_values(from_value=5000, to_value=10000),
			orders_about_issued_pay_values_5000_10000=self._orders_about_issued_pay_values(from_value=5000, to_value=10000),

			payed_orders_10000_30000=self._count_payed_orders(from_value=10000, to_value=30000),
			canceled_orders_10000_30000=self._count_canceled_orders(from_value=10000, to_value=30000),
			issued_requisites_10000_30000=self._count_issued_requisites(from_value=10000, to_value=30000),
			orders_about_issued_requisites_10000_30000=self._orders_about_issued_requisites(from_value=10000, to_value=30000),
			issued_pay_values_10000_30000=self._count_issued_pay_values(from_value=10000, to_value=30000),
			orders_about_issued_pay_values_10000_30000=self._orders_about_issued_pay_values(from_value=10000, to_value=30000),

			payed_orders_30000_50000=self._count_payed_orders(from_value=30000, to_value=50000),
			canceled_orders_30000_50000=self._count_canceled_orders(from_value=30000, to_value=50000),
			issued_requisites_30000_50000=self._count_issued_requisites(from_value=30000, to_value=50000),
			orders_about_issued_requisites_30000_50000=self._orders_about_issued_requisites(from_value=30000, to_value=50000),
			issued_pay_values_30000_50000=self._count_issued_pay_values(from_value=30000, to_value=50000),
			orders_about_issued_pay_values_30000_50000=self._orders_about_issued_pay_values(from_value=30000, to_value=50000),

			payed_orders_50000_=self._count_payed_orders(from_value=50000),
			canceled_orders_50000_=self._count_canceled_orders(from_value=50000),
			issued_requisites_50000_=self._count_issued_requisites(from_value=50000),
			orders_about_issued_requisites_50000_=self._orders_about_issued_requisites(from_value=50000),
			issued_pay_values_50000_=self._count_issued_pay_values(from_value=50000),
			orders_about_issued_pay_values_50000_=self._orders_about_issued_pay_values(from_value=50000),

			pidors_count=self._pidors_count()
		)

		bot.send_message(channel_id, mess, parse_mode='HTML')


















