# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from telegram.models import Client, Order, WorkingShift, Transaction, Purchase, Promocode
import json
from django.utils.timezone import datetime

class Command(BaseCommand):
	help = 'Загрузка дампа бд'

	def dump_users(self):
		with open('dump.json') as file:
			dump = json.load(file)

		ban_list = dump['user:0:ban-list']
		u_ids = dump['user:0:U-IDS23-01-22']
		for u_id in u_ids:
			if int(u_id) == 1057:
				continue

			fields = []
			for key in dump:
				if str(u_id) in key and len(key.split(':')) > 1:
					fields.append(key.split(':')[-1])

			if 'count' in fields:
				count = dump[f'user:{u_id}:count']
			else:
				count = 0

			if 'reffer' in fields:
				father = int(dump[f'user:{u_id}:reffer'])
			else:
				father = None

			if 'reffer-cash' in fields:
				ref_profit = round(dump[f'user:{u_id}:reffer-cash'])
			else:
				ref_profit = 0

			if 'count-ref' in fields:
				ref_count = dump[f'user:{u_id}:count-ref']
			else:
				ref_count = 0

			if 'used-promocodes' in fields:
				old_promocodes = ';'.join(dump[f'user:{u_id}:used-promocodes'])
			else:
				old_promocodes = None

			if 'active-promocodes' in fields:
				active_promocodes = ';'.join(dump[f'user:{u_id}:active-promocodes'])
			else:
				active_promocodes = None

			ban = str(u_id) in ban_list

			if Client.objects.filter(tg_id=int(u_id)).exists():
				client = Client.objects.get(tg_id=int(u_id))
				client.father = father
				client.count = int(count)
				client.ref_profit = int(ref_profit)
				client.ref_count = int(ref_count)
				client.active_promocodes = active_promocodes
				client.old_promocodes = old_promocodes
				client.ban = ban
				client.save()
			else:
				client = Client.objects.create(
					father=father,
					tg_id=int(u_id),
					username=None,
					count=int(count),
					ref_profit=int(ref_profit),
					ref_count=int(ref_count),
					register_date=datetime.now(),
					active_promocodes=active_promocodes,
					old_promocodes=old_promocodes,
					ban=ban
				)

	def dump_promocodes(self):
		with open('dump.json') as file:
			dump = json.load(file)

		promocodes = dump['user:0:promo']
		for name in promocodes:
			one_off = not name.endswith('!')
			discount = promocodes[name]
			count = 0

			for client in Client.objects.all():
				if name in client.get_old_promocodes() or name in client.get_active_promocodes():
					count += 1

			if Promocode.objects.filter(name=name).exists():
				promocode = Promocode.objects.get(name=name)
				promocode.discount = discount
				promocode.in_fiat = True
				promocode.one_off = one_off
				promocode.count = count
				promocode.save()
			else:
				promocode = Promocode.objects.create(
					name=name,
					discount=discount,
					in_fiat=True,
					one_off=one_off,
					count=count
				)

	def handle(self, *args, **options):
		self.dump_users()
		self.dump_promocodes()



















