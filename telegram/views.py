from django.shortcuts import render
from general_settings.models import PaymentMethod, GeneralSettings, CryptSettings, RequisitesRequest
from django.http import HttpResponse, HttpResponseRedirect
from .handler import sms_bot as bot
import re
from django.utils.timezone import datetime
from datetime import timedelta
from telegram.models import Notification, Order, Client, Wallet, WalletTransaction
from telegram.modules_admin import messages
import telebot
import logging, traceback
import os
from django.conf import settings as django_settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from dotenv import load_dotenv
from django.core.cache import cache
import time, random
from decimal import Decimal
from .handler import bot as main_bot
from telegram.modules import messages as client_messages
from wallets import BTCWallet, LTCWallet, XMRWallet, USDTWallet

wallets = {
    'BTC': BTCWallet.Wallet,
    'LTC': LTCWallet.Wallet,
    'XMR': XMRWallet.Wallet,
    'USDT': USDTWallet.Wallet
}

load_dotenv()

logger_notifications = logging.getLogger('NOTIFICATIONS')

# Create your views here.
@csrf_exempt
@require_POST
def update(request):
	token = request.headers['X-Telegram-Bot-Api-Secret-Token']
	if token != django_settings.WEBHOOK_TOKEN:
		return HttpResponse(status=400)

	json_str = request.body.decode('UTF-8')
	update = telebot.types.Update.de_json(json_str)
	bot.process_new_updates([update])
	return HttpResponse('OK', status=200)


def restart(request):
	if request.user and request.user.is_superuser:
		try:
			os.system('supervisorctl restart all')
		except Exception as e:
			print(e)
		return HttpResponseRedirect('/admin/')

	return HttpResponse(status=400)


# @csrf_exempt
# @require_POST
# def payok_callback(request):
# 	data = json.loads(request.body.decode('utf-8'))
# 	if os.environ['PAYOK_EMAIL'] != data['email']:
# 		return HttpResponse(status=403)

# 	if data['transaction_status'] == 1:
# 		admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)
# 		notification = Notification.objects.create(
# 			bank='Банк РФ',
# 			notification_type='Пополнение',
# 			pay=data['amount'],
# 			balance=0,
# 			datetime=datetime.now(),
# 			confirmed=True,
# 			label=str(data['payment_id'])
# 		)

# 		bot.send_message(admin, f'PAYOK ID: <code>{notification.label}</code>\n✅💸 <b>Подтвержденное пополнение</b> <code>{notification.pay}</code> RUB.')

# 		payment_method = PaymentMethod.objects.first()
# 		payment_method.payok_balance += notification.pay
# 		payment_method.save()
		
# 	return HttpResponse(200)


@csrf_exempt
def alfateam_callback(request):
    data = json.loads(request.body.decode('utf-8'))
    if data['notificationType'] == 'invoice' and data['invoice']['status'] == 'paid':
        admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)
        notification, created = Notification.objects.get_or_create(
            pay=int(data['invoice']['sum']['amount'].replace('.00', '')),
            label=data['invoice']['id'],
            defaults={
                'bank': data['invoice']['deal']['paymentMethod'],
                'notification_type': 'Пополнение',
                'pay': int(data['invoice']['sum']['amount'].replace('.00', '')),
                'balance': 0,
                'datetime': datetime.now(),
                'confirmed': True,
                'label': data['invoice']['id']
            }
        )
        if created:
            try:
                bot.send_message(admin, f'ALFATEAM ID: <code>{notification.label}</code>\nБанк: {notification.bank}\n✅💸 Подтвержденное пополнение {notification.pay} RUB')
                payment_method = PaymentMethod.objects.get(id=1)
                payment_method.alfateam_balance += notification.pay
                payment_method.save()
            except:
                pass
            
    return HttpResponse(200)


@csrf_exempt
def pspware_callback(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        logger_notifications.info(data)

        if data['status'] == 'success':
            admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)
            notification, created = Notification.objects.get_or_create(
                pay=int(float(data['sum'])),
                label=data['id'],
                defaults={
                    'bank': 'Банк РФ',
                    'notification_type': 'Пополнение',
                    'pay': int(float(data['sum'])),
                    'balance': 0,
                    'datetime': datetime.now(),
                    'confirmed': True,
                    'label': data['id']
                }
            )

            if created:
                bot.send_message(admin, f'PSPWARE ID: <code>{notification.label}</code>\nБанк: {notification.bank}\n✅💸 Подтвержденное пополнение {notification.pay} RUB')

                payment_method = PaymentMethod.objects.get(id=1)
                payment_method.pspware_balance += notification.pay
                payment_method.save()

    except:
        logger_notifications.error({'pspware error': traceback.format_exc()})

    return HttpResponse(200)


def secrett_callback(request):
    data = request.GET
    logger_notifications.info(data)

    try:
        request_id = str(data['id'])
        status = data['status']

        if status == 'COMPLETED':
            print(request_id, status)
            requisites_request = RequisitesRequest.objects.filter(provider='secrett', request_id=request_id).last()

            if requisites_request is not None:
                admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)
                notification, created = Notification.objects.get_or_create(
                    pay=requisites_request.amount,
                    label=requisites_request.label,
                    defaults={
                        'bank': 'Банк РФ',
                        'notification_type': 'Пополнение',
                        'pay': requisites_request.amount,
                        'balance': 0,
                        'datetime': datetime.now(),
                        'confirmed': True,
                        'label': requisites_request.label
                    }
                )

                if created:
                    try:
                        bot.send_message(admin, f'SECRETT ID: <code>{notification.label}</code>\n✅💸 <b>Подтвержденное пополнение</b> <code>{notification.pay}</code> RUB')

                        payment_method = PaymentMethod.objects.first()
                        payment_method.secrett_balance += notification.pay
                        payment_method.save()

                    except:
                        print(traceback.format_exc())
                        pass

    except:
        logger_notifications.error({'provider': 'secrett', 'error': traceback.format_exc()})

    return HttpResponse(200)


@csrf_exempt
def xpay_callback(request):
	body = request.body.decode('utf-8')
	if body == '':
		return HttpResponse(200)

	data = json.loads(body)
	if data['tx']['tx_status'] in ['TX_SUCCESS', 'TX_RECALCULATED']:
		admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)
		notification = Notification.objects.create(
			bank=data['tx']['payment_system'],
			notification_type='Пополнение',
			pay=int(data['tx']['in_amount']),
			balance=0,
			datetime=datetime.now(),
			confirmed=True,
			label=data['tx']['tx_id']
		)
		bot.send_message(admin, f'XPAY ID: <code>{notification.label}</code>\nБанк: {notification.bank}\n✅💸 Подтвержденное пополнение {notification.pay} RUB')

		payment_method = PaymentMethod.objects.get(id=1)
		payment_method.xpay_balance += notification.pay
		payment_method.save()
		
	return HttpResponse(200)


@csrf_exempt
def onlypays_callback(request):
	data = json.loads(request.body.decode('utf-8'))

	if data['status'] == 'finished':
		admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)
		notification = Notification.objects.create(
			bank='Банк РФ',
			notification_type='Пополнение',
			pay=int(data['received_sum']),
			balance=0,
			datetime=datetime.now(),
			confirmed=True,
			label=data['id']
		)
		bot.send_message(admin, f'ONLYPAYS ID: <code>{notification.label}</code>\nБанк: {notification.bank}\n✅💸 Подтвержденное пополнение {notification.pay} RUB')

		payment_method = PaymentMethod.objects.get(id=1)
		payment_method.onlypays_balance += notification.pay
		payment_method.save()

		# try:
		# 	order = Order.objects.get(label=notification.label, status='timeouted', provider='onlypays')
		# 	order.datetime = datetime.now()
		# 	order.status = 'pending'
		# 	order.save()

		# except Order.DoesNotExist:
		# 	print('DoesNotExist')

	return HttpResponse(200)


@csrf_exempt
def bridgepay_callback(request):
	data = json.loads(request.body.decode('utf-8'))

	if data['notificationType'] == 'invoice' and data['invoice']['status'] == 'paid':
		admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)
		notification, created = Notification.objects.get_or_create(
			pay=int(data['invoice']['sum']['amount'].replace('.00', '')),
			label=data['invoice']['id'],
			defaults={
				'bank': data['invoice']['deal']['paymentMethod'],
				'notification_type': 'Пополнение',
				'pay': int(data['invoice']['sum']['amount'].replace('.00', '')),
				'balance': 0,
				'datetime': datetime.now(),
				'confirmed': True,
				'label': data['invoice']['id']
			}
		)
		if created:
			try:
				bot.send_message(admin, f'BRIDGEPAY ID: <code>{notification.label}</code>\nБанк: {notification.bank}\n✅💸 Подтвержденное пополнение {notification.pay} RUB')

				payment_method = PaymentMethod.objects.get(id=1)
				payment_method.bridgepay_balance += notification.pay
				payment_method.save()
			except:
				pass
		
	return HttpResponse(200)


@csrf_exempt
def bridgepay_tj_callback(request):
	data = json.loads(request.body.decode('utf-8'))

	if data['notificationType'] == 'invoice' and data['invoice']['status'] == 'paid':
		admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)
		notification, created = Notification.objects.get_or_create(
			pay=int(data['invoice']['sum']['amount'].replace('.00', '')),
			label=data['invoice']['id'],
			defaults={
				'bank': data['invoice']['deal']['paymentMethod'],
				'notification_type': 'Пополнение',
				'pay': int(data['invoice']['sum']['amount'].replace('.00', '')),
				'balance': 0,
				'datetime': datetime.now(),
				'confirmed': True,
				'label': data['invoice']['id']
			}
		)
		if created:
			try:
				bot.send_message(admin, f'BRIDGEPAY-TJ ID: <code>{notification.label}</code>\nБанк: {notification.bank}\n✅💸 Подтвержденное пополнение {notification.pay} RUB')

				payment_method = PaymentMethod.objects.get(id=1)
				payment_method.bridgepay_tj_balance += notification.pay
				payment_method.save()
			except:
				pass
		
	return HttpResponse(200)


@csrf_exempt
def merchant001_callback(request):
    data = json.loads(request.body.decode('utf-8'))
    logger_notifications.info(data)

    try:
        if data['status'] == 'CONFIRMED':
            admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)
            notification, created = Notification.objects.get_or_create(
                pay=int(data['transaction']['pricing']['local']['amount']),
                label=str(data['transaction']['id']),
                defaults={
                    'bank': data['transaction']['selectedProvider']['method'],
                    'notification_type': 'Пополнение',
                    'pay': int(data['transaction']['pricing']['local']['amount']),
                    'balance': 0,
                    'datetime': datetime.now(),
                    'confirmed': True,
                    'label': str(data['transaction']['id'])
                }
            )

            if created:
                try:
                    bot.send_message(admin, f'MERCHANT001 ID: <code>{notification.label}</code>\nБанк: {notification.bank}\n✅💸 <b>Подтвержденное пополнение</b> <code>{notification.pay}</code> RUB')

                    payment_method = PaymentMethod.objects.first()
                    payment_method.merchant001_balance += notification.pay
                    payment_method.save()
                except:
                    pass

    except:
        logger_notifications.error({'provider': 'merchant001', 'error': traceback.format_exc()})
        
    return HttpResponse(200)


@csrf_exempt
def bitzone_callback(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        logger_notifications.info(data)

        if data['status'] in ['re_calculation', 'closed']:
            admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)
            notification, created = Notification.objects.get_or_create(
                pay=int(float(data['fiatAmount'])),
                label=data['id'],
                defaults={
                    'bank': 'Банк РФ',
                    'notification_type': 'Пополнение',
                    'pay': int(float(data['fiatAmount'])),
                    'balance': 0,
                    'datetime': datetime.now(),
                    'confirmed': True,
                    'label': data['id']
                }
            )

            if created:
                bot.send_message(admin, f'BITZONE ID: <code>{notification.label}</code>\nБанк: {notification.bank}\n✅💸 Подтвержденное пополнение {notification.pay} RUB')

                payment_method = PaymentMethod.objects.get(id=1)
                payment_method.bitzone_balance += notification.pay
                payment_method.save()

    except:
        logger_notifications.error({'bitzone error': traceback.format_exc()})

    return HttpResponse(200)

@csrf_exempt
def wellbit_callback(request):
    try:
        raw = request.body.decode('utf-8')
        if not raw:
            logger_notifications.error('wellbit_callback: empty body')
            return HttpResponse(status=400)

        data = json.loads(raw)
        logger_notifications.info(data)

        payment = data.get('payment', {})
        status = payment.get('status')
        if status == 'new':
            amount = int(float(payment.get('amount_to_balance', 0)))
            label  = payment.get('id')

            admin_tg = GeneralSettings.objects.first().admin_tg_id
            admin    = Client.objects.get(tg_id=admin_tg)

            notification, created = Notification.objects.get_or_create(
                pay=amount,
                label=label,
                defaults={
                    'bank': 'Банк РФ',
                    'notification_type': 'Пополнение',
                    'pay': amount,
                    'balance': 0,
                    'datetime': datetime.now(),
                    'confirmed': True,
                    'label': label
                }
            )

            if created:
                bot.send_message(
                    admin,
                    f'WELLBIT ID: <code>{label}</code>\n'
                    f'Банк: {notification.bank}\n'
                    f'✅💸 Подтвержденное пополнение {amount} RUB'
                )
                payment_method = PaymentMethod.objects.get(id=1)
                payment_method.wellbit_balance += amount
                payment_method.save()

    except json.JSONDecodeError:
        logger_notifications.error({'wellbit_callback': f'invalid JSON: {raw}'})
        return HttpResponse(status=400)
    except Exception:
        logger_notifications.error({'wellbit_callback_error': traceback.format_exc()})

    return HttpResponse(status=200)


@csrf_exempt
def extasypay_callback(request):
    data = json.loads(request.body.decode('utf-8'))
    logger_notifications.info(data)

    try:
        if data['status'] == 'paid':
            admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)
            notification, created = Notification.objects.get_or_create(
                pay=int(float(data['amount'])),
                label=str(data['id']),
                defaults={
                    'bank': 'Банк РФ',
                    'notification_type': 'Пополнение',
                    'pay': int(float(data['amount'])),
                    'balance': 0,
                    'datetime': datetime.now(),
                    'confirmed': True,
                    'label': str(data['id'])
                }
            )

            if created:
                try:
                    bot.send_message(admin, f'EXTASYPAY ID: <code>{notification.label}</code>\n✅💸 <b>Подтвержденное пополнение</b> <code>{notification.pay}</code> RUB')

                    payment_method = PaymentMethod.objects.first()
                    payment_method.extasypay_balance += notification.pay
                    payment_method.save()

                except:
                    pass

    except:
        logger_notifications.error({'provider': 'extasypay', 'error': traceback.format_exc()})

    return HttpResponse(200)


@csrf_exempt
def collybus_callback(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        logger_notifications.info(data)

        if data['status'] == 'success':
            admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)
            notification, created = Notification.objects.get_or_create(
                pay=int(data['initial_amount']),
                label=data['id'],
                defaults={
                    'bank': 'Банк СНГ',
                    'notification_type': 'Пополнение',
                    'pay': int(data['initial_amount']),
                    'balance': 0,
                    'datetime': datetime.now(),
                    'confirmed': True,
                    'label': data['id']
                }
            )

            if created:
                bot.send_message(admin, f'Банк: {notification.bank}\n✅💸 Подтвержденное пополнение {notification.pay} RUB')

                payment_method = PaymentMethod.objects.get(id=1)
                payment_method.collybus_balance += notification.pay
                payment_method.save()

    except:
        logger_notifications.error({'collybus error': traceback.format_exc()})

    return HttpResponse(200)


@csrf_exempt
def infinitypay_callback(request):
    data = json.loads(request.body.decode('utf-8'))
    logger_notifications.info(data)

    try:
        if data['status'] == 'success':
            admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)
            notification, created = Notification.objects.get_or_create(
                pay=int(data['order_amount'] / 100),
                label=data['order_hash'],
                defaults={
                    'bank': 'Банк РФ',
                    'notification_type': 'Пополнение',
                    'pay': int(data['order_amount'] / 100),
                    'balance': 0,
                    'datetime': datetime.now(),
                    'confirmed': True,
                    'label': data['order_hash']
                }
            )

            if created:
                try:
                    bot.send_message(admin, f'INFINITYPAY ID: <code>{notification.label}</code>\n✅💸 <b>Подтвержденное пополнение</b> <code>{notification.pay}</code> RUB')

                    payment_method = PaymentMethod.objects.first()
                    payment_method.infinitypay_balance += notification.pay
                    payment_method.save()

                except:
                    pass

    except:
        logger_notifications.error({'provider': 'infinitypay', 'error': traceback.format_exc()})

    return HttpResponse(200)

@csrf_exempt
def vita_callback(request):
    data = json.loads(request.body.decode('utf-8'))
    logger_notifications.info(data)

    try:
        if data['status'] == 'success':
            admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)
            notification, created = Notification.objects.get_or_create(
                pay=int(float(data['final_amount'])),
                label=str(data['id']),
                defaults={
                    'bank': 'Банк РФ',
                    'notification_type': 'Пополнение',
                    'pay': int(float(data['final_amount'])),
                    'balance': 0,
                    'datetime': datetime.now(),
                    'confirmed': True,
                    'label': str(data['id'])
                }
            )

            if created:
                try:
                    bot.send_message(admin, f'VITA ID: <code>{notification.label}</code>\n✅💸 <b>Подтвержденное пополнение</b> <code>{notification.pay}</code> RUB')

                    payment_method = PaymentMethod.objects.first()
                    payment_method.vita_balance += notification.pay
                    payment_method.save()

                except:
                    pass

    except:
        logger_notifications.error({'provider': 'vita', 'error': traceback.format_exc()})

    return HttpResponse(200)


def notification_handler(payment_method_id, pay, balance, debit=False, bank='Tinkoff'):
	try:
		admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)
		payment_method = PaymentMethod.objects.get(id=payment_method_id)
		if debit:
			notification = Notification.objects.create(
				bank=bank,
				notification_type='Списание',
				pay=pay,
				balance=balance,
				datetime=datetime.now(),
				confirmed=True
			)
			# if payment_method.balance == round(balance+pay, 2):
			# 	payment_method.balance = balance
			# 	payment_method.save()

			bot.send_message(admin, f'Банк: {bank}\n📲💸 <b>Списание</b> <code>{pay}</code> RUB. Баланс: <code>{balance}</code> RUB')
		else:
			# if payment_method.balance == round(balance-pay, 2):
			# 	confirmed = True
			# 	payment_method.balance = balance
			# 	payment_method.save()
				
			# else:
			# 	confirmed = False

			confirmed = True

			notification = Notification.objects.create(
				bank=bank,
				notification_type='Пополнение',
				pay=pay,
				balance=balance,
				datetime=datetime.now(),
				confirmed=confirmed
			)
			if confirmed:
				bot.send_message(admin, f'Банк: {bank}\n✅💸 <b>Подтвержденное пополнение</b> <code>{pay}</code> RUB. Баланс: <code>{balance}</code> RUB')
			else:
				menu = telebot.types.InlineKeyboardMarkup()
				menu.row(
					telebot.types.InlineKeyboardButton(text='Подтвердить пополнение', callback_data=f'confirm_notification-{notification.id}')
				)
				bot.send_message(admin, f'Банк: {bank}\n❓💸 <b>Неподтвержденное пополнение</b> <code>{pay}</code> RUB. Баланс: <code>{balance}</code> RUB', reply_markup=menu)
	except Exception as e:
		logger_notifications.error(e)

def notification(request, payment_method_id):
	payment_method_id = int(payment_method_id)
	sms = request.GET['sms']

	time.sleep(random.choice([x / 10.0 for x in range(21)]))

	if cache.get(sms):
		return HttpResponse('dublicate')

	cache.set(sms, True, 900)

	logger_notifications.info(sms)
	if 'Пополнение,' in sms:
		temp = r'Пополнение, счет RUB. (.*) RUB.(.*)Доступно (.*) RUB'
		payment_result = re.search(temp, sms)
		pay = float(payment_result[1].replace(' ', '').replace(',', '.').replace('\xa0', ''))
		balance = float(payment_result[3].replace(' ', '').replace(',', '.').replace('\xa0', ''))
		notification_handler(payment_method_id, pay, balance)

	elif 'Пополнение на' in sms:
		temp = r'Пополнение на (.*) Р, счет RUB. (.*) Доступно (.*) Р'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(1).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		balance = float(payment_result.group(3).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		notification_handler(payment_method_id, pay, balance)

	elif 'Пришел перевод на счет' in sms:
		temp = r'Пришел перевод на счет (.*) Р от (.*), (.*) Теперь на счете (.*) Р'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(1).replace(' ', '')[5:].replace(',', '.').replace('\xa0', ''))
		balance = float(payment_result.group(4).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		notification_handler(payment_method_id, pay, balance, bank='Raiffeisen')

	elif 'перевод' in sms and 'на карту' in sms and 'Баланс' in sms:
		temp = r'(.*) перевод (.*)р на карту (.*) Баланс (.*) TRANSFER, (.*)'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(2).replace(' ', '').replace(',', '').replace('\xa0', ''))
		balance = float(payment_result.group(4).replace(' ', '').replace(',', '').replace('\xa0', ''))
		notification_handler(payment_method_id, pay, balance, bank='Rshb')

	elif 'Перевод. Счет' in sms:
		temp = r'Перевод.\sСчет RUB.\s(.*)\sRUB.(.*)Баланс\s(.*)\sRUB'
		payment_result = re.search(temp, sms)
		pay = float(payment_result.group(1).replace(" ", ""))
		balance = float(payment_result.group(3).replace(" ", ""))
		notification_handler(payment_method_id, pay, balance, debit=True)

	elif 'Перевод на сумму' in sms:
		temp = r'Перевод на сумму (.*) RUR из (.*) от (.*) по СБП.'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(1).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		balance = -1
		notification_handler(payment_method_id, pay, balance, bank='Alfa')

	elif 'Перевод на' in sms:
		payment_result = re.search(r'Перевод на (.*) ₽, счет RUB.', sms)
		pay = float(payment_result.group(1).replace(' ', '').replace('\xa0', ''))
		balance_result = re.search(r'Баланс (.*) ₽', sms)
		balance = float(balance_result.group(1).replace(' ', '').replace('\xa0', ''))
		notification_handler(payment_method_id, pay, balance, debit=True)

	elif 'Покупка,' in sms:
		temp = r'Покупка, карта(.*). (.*)\sRUB. (.*). Доступно (.*)\sRUB'
		payment_result = re.search(temp, sms)
		pay = float(payment_result.group(2).replace(" ", ""))
		balance = float(payment_result.group(4).replace(" ", ""))
		notification_handler(payment_method_id, pay, balance, debit=True)
	elif 'Платеж на' in sms:
		pay_balance = re.search(r'Платеж на\s(.*) ₽, счет RUB\sБаланс(.*)\s₽', sms)
		pay = float(pay_balance[1].replace('\xa0', '').replace(" ", ""))
		balance = float(pay_balance[2].replace('\xa0', '').replace(" ", ""))
		notification_handler(payment_method_id, pay, balance, debit=True)

	elif '- Баланс:' in sms:
		temp = r'(.*) ₽ - Баланс: (.*) ₽ (.*)'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(1).replace(' ', '').replace(',', '.'))
		balance = float(payment_result.group(2).replace(' ', '').replace(',', '.'))
		notification_handler(payment_method_id, pay, balance, bank='Sber')

	elif 'Оплата' in sms:
		temp = r'(.*) (.*) Оплата (.*)р Баланс: (.*)р'
		payment_result = re.search(temp, sms)
		if payment_result:
			pay = float(payment_result.group(3).replace(' ', '').replace(',', '.'))
			balance = float(payment_result.group(4).replace(' ', '').replace(',', '.'))
			notification_handler(payment_method_id, pay, balance, debit=True, bank='Sber')
		else:
			temp = r'(.*) (.*) Оплата (.*)р (.*) Баланс: (.*)р'
			payment_result = re.search(temp, sms)
			pay = float(payment_result.group(3).replace(' ', '').replace(',', '.'))
			balance = float(payment_result.group(5).replace(' ', '').replace(',', '.'))
			notification_handler(payment_method_id, pay, balance, debit=True, bank='Sber')

	elif 'Пополнили карту' in sms:
		temp = r'Пополнили карту (.*) (.*) Р. Теперь на карте (.*) Р'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(2).replace(' ', '').replace(',', '.'))
		balance = float(payment_result.group(3).replace(' ', '').replace(',', '.'))
		notification_handler(payment_method_id, pay, balance, bank='Raiffeisen')
		# temp = r'[-+]?(?:\d*\.*\d+)'
		# payment_result = re.findall(temp, sms)

		# pay = float(payment_result[2])
		# balance = float(payment_result[3])
		# notification_handler(payment_method_id, pay, balance, bank='Raiffeisen')

	elif 'Перевод' in sms and ' от ' in sms and ' из ' in sms and '— Баланс' in sms:
		try:
			temp = r'Перевод из (.*) +(.*)р от (.*) (.*) — Баланс: (.*)р'
			payment_result = re.search(temp, sms)

			pay = float(payment_result.group(2).replace(' ', '').replace(',', '.').replace('\xa0', '').replace('+', ''))
			balance = float(payment_result.group(5).replace(' ', '').replace(',', '.').replace('\xa0', ''))

		except:
			temp = r'Перевод из (.*) +(.*)р от (.*) (.*) — Баланс: (.*)р (.*)'
			payment_result = re.search(temp, sms)

			balance = float(payment_result.group(5).replace(' ', '').replace(',', '.').replace('\xa0', ''))
			pay = float(payment_result.group(2).replace(' ', '').replace(',', '.').replace('\xa0', '').replace('+', ''))


		notification_handler(payment_method_id, pay, balance, bank='Sber')

	elif 'Перевод' in sms and ' от ' in sms and ' из ' in sms:
		if 'Баланс' in sms:
			# temp = r'(.*) (.*) Перевод из (.*) (.*)р от (.*) Баланс: (.*)р'
			# payment_result = re.search(temp, sms)

			# pay = float(payment_result.group(4).replace(' ', '').replace(',', '.').replace('\xa0', ''))
			# balance = float(payment_result.group(6).replace(' ', '').replace(',', '.').replace('\xa0', ''))

			# pay_result = re.search(r'(.*)р', sms)
			# pay = float(pay_result.group(1).replace(' ', '').replace(',', '.').replace('\xa0', ''))

			# balance = -1

			temp = r'[-+]?(?:\d*\.*\d+)'
			payment_result = re.findall(temp, sms)

			pay = float(payment_result[3])
			balance = float(payment_result[4])
		else:
			try:
				temp = r'(.*) (.*) Перевод (.*)р из (.*) от (.*)'
				payment_result = re.search(temp, sms)

				pay = float(payment_result.group(3).replace(' ', '').replace(',', '.'))
				balance = -1
			except:
				temp = r'Перевод из (.*) (.*)р от (.*)'
				payment_result = re.search(temp, sms)

				pay = float(payment_result.group(2).replace(' ', '').replace(',', '.').replace('+', ''))
				balance = -1

		notification_handler(payment_method_id, pay, balance, bank='Sber')

	elif 'Platezh s nomera' in sms:
		temp = r'Schet (.*). Platezh s nomera (.*). Summa (.*) RUB. Balans (.*) RUB.'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(3).replace(' ', '').replace(',', '.'))
		balance = float(payment_result.group(4).replace(' ', '').replace(',', '.'))
		notification_handler(payment_method_id, pay, balance, bank='Raiffeisen')

	elif 'Zachisleno' in sms:
		temp = r'Karta (.*). Zachisleno (.*) RUB. Balans (.*) RUB. (.*)'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(2).replace(' ', '').replace(',', '.'))
		balance = float(payment_result.group(3).replace(' ', '').replace(',', '.'))
		notification_handler(payment_method_id, pay, balance, bank='Raiffeisen')

	elif 'и сообщение' in sms:
		temp = r'(.*) ₽ и сообщение «(.*)» от (.*), (.*) Теперь на счете (.*) ₽'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(1).replace(' ', '').replace(',', '.').replace('+', ''))
		balance = float(payment_result.group(5).replace(' ', '').replace(',', '.').replace('+', ''))
		notification_handler(payment_method_id, pay, balance, bank='Raiffeisen')

	elif 'Теперь на счете' in sms and 'Р' in sms:
		temp = r'(.*) Р от (.*) Теперь на счете (.*) Р'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(1).replace(' ', '').replace(',', '.'))
		balance = float(payment_result.group(3).replace(' ', '').replace(',', '.'))
		notification_handler(payment_method_id, pay, balance, bank='Raiffeisen')

	elif 'Теперь на счете' in sms and '₽' in sms:
		temp = r'(.*) ₽ от (.*) Теперь на счете (.*) ₽'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(1).replace(' ', '').replace(',', '.'))
		balance = float(payment_result.group(3).replace(' ', '').replace(',', '.'))
		notification_handler(payment_method_id, pay, balance, bank='Raiffeisen')

	elif 'Теперь на карте' in sms:
		temp = r'(.*) ₽(.*) Теперь на карте (.*) ₽'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(1).replace(' ', '').replace(',', '.'))
		balance = float(payment_result.group(3).replace(' ', '').replace(',', '.'))
		notification_handler(payment_method_id, pay, balance, bank='Raiffeisen')

	elif 'Popolnenie' in sms:
		temp = r'Popolnenie (.*) na (.*) RUR Balans (.*) RUR (.*)'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(2).replace(' ', '').replace(',', '.'))
		balance = float(payment_result.group(3).replace(' ', '').replace(',', '.'))
		notification_handler(payment_method_id, pay, balance, bank='Alfa')

	elif 'зачисление на сумму' in sms:
		temp = r'зачисление на сумму (.*)р. (.*).'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(1).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		balance = -1
		notification_handler(payment_method_id, pay, balance, bank='OTP')

	elif 'otpbank.ru' in sms:
		temp = r'Карта (.*) зачисление (.*)р. (.*). Доступно (.*)р. (.*)'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(2).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		balance = float(payment_result.group(4).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		notification_handler(payment_method_id, pay, balance, bank='OTP')

	elif 'зачисление' in sms:
		temp = r'(.*) (.*) зачисление (.*)р Баланс: (.*)р'
		payment_result = re.search(temp, sms)
		if payment_result:
			pay = float(payment_result.group(3).replace(' ', '').replace(',', '.').replace('\xa0', ''))
			balance = float(payment_result.group(4).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		else:
			temp = r'(.*) (.*) зачисление (.*)р (.*) Баланс: (.*)р'
			payment_result = re.search(temp, sms)
			pay = float(payment_result.group(3).replace(' ', '').replace(',', '.').replace('\xa0', ''))
			balance = float(payment_result.group(5).replace(' ', '').replace(',', '.').replace('\xa0', ''))

		notification_handler(payment_method_id, pay, balance, bank='Sber')

	elif 'Успешный перевод' in sms:
		temp = r'Успешный перевод СБП. (.*) из (.*) Зачислено (.*)RUR'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(3).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		balance = -1
		notification_handler(payment_method_id, pay, balance, bank='Rshb')

	elif 'Перевод' in sms and 'от' in sms:
		if 'Баланс' in sms:
			temp = r'(.*) (.*) Перевод (.*)р от (.*) Баланс: (.*)р'
			payment_result = re.search(temp, sms)

			pay = float(payment_result.group(3).replace(' ', '').replace(',', '.').replace('\xa0', ''))
			balance = float(payment_result.group(5).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		else:
			temp = r'(.*) (.*) Перевод (.*)р от (.*)'
			payment_result = re.search(temp, sms)

			pay = float(payment_result.group(3).replace(' ', '').replace(',', '.').replace('\xa0', ''))
			balance = -1

		notification_handler(payment_method_id, pay, balance, bank='Sber')

	elif 'зачислен перевод по СБП' in sms:
		return HttpResponse('ok')

		temp = r'(.*) (.*) зачислен перевод по СБП (.*)р из (.*) от (.*)'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(3).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		balance = -1
		notification_handler(payment_method_id, pay, balance, bank='Sber')

	elif 'зачислен перевод' in sms:
		temp = r'(.*) (.*) зачислен перевод (.*)р из (.*) от (.*)'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(3).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		notification_handler(payment_method_id, pay, -1, bank='Sber')

	elif 'Получен перевод' in sms:
		temp = r'(.*) Получен перевод (.*)р (.*) Доступно (.*)р'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(2).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		balance = float(payment_result.group(4).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		notification_handler(payment_method_id, pay, balance, bank='Gazprombank')

	elif 'Перевод' in sms and 'Доступно' in sms:
		temp = r'(.*) Перевод (.*)р (.*) Доступно (.*)р'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(2).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		balance = float(payment_result.group(4).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		notification_handler(payment_method_id, pay, balance, bank='Gazprombank')

	elif 'перевод' in sms:
		temp = r'(.*) (.*) перевод (.*)р (.*) Баланс: (.*)р'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(3).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		balance = float(payment_result.group(5).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		notification_handler(payment_method_id, pay, balance, bank='Sber', debit=True)

	elif 'Zachislen perevod' in sms:
		temp = r'(.*) (.*) Zachislen perevod (.*) RUB. Balans (.*) RUB.'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(3).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		balance = float(payment_result.group(4).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		notification_handler(payment_method_id, pay, balance, bank='Sber')

	elif 'перевел(а) вам' in sms:
		return HttpResponse('ok')

		temp = r'(.*) (.*) (.*) (.*)р.'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(4).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		balance = -1
		notification_handler(payment_method_id, pay, balance, bank='Sber')

	elif '"Перевод денежных средств"' in sms:
		temp = r'(.*)   (.*) ₽ (.*) •• (.*) "Перевод денежных средств"'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(2).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		balance = -1
		notification_handler(payment_method_id, pay, balance, bank='Sber')

	elif 'Пополнение через' in sms:
		temp = r'Пополнение через СБП. Карта (.*). Сумма: (.*) RUR.'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(2).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		balance = -1
		notification_handler(payment_method_id, pay, balance, bank='Akbars')

	elif 'Зачисление СБП' in sms:
		temp = r'Зачисление СБП: (.*) р от (.*)'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(1).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		balance = -1
		notification_handler(payment_method_id, pay, balance, bank='Uralsib')

	elif 'Зачислено через СБП' in sms:
		temp = r'Зачислено через СБП (.*)RUB.'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(1).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		balance = -1
		notification_handler(payment_method_id, pay, balance, bank='OTP')

	elif 'Поступление' in sms and 'Остаток' in sms:
		temp = r'(.*) ₽.Поступление Остаток: (.*) ₽; (.*)'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(1).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		balance = float(payment_result.group(2).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		notification_handler(payment_method_id, pay, balance, bank='Alfa')

	elif 'Поступление' in sms and 'через СБП' in sms:
		temp = r'Поступление (.*)р. (.*) через СБП.'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(1).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		balance = -1
		notification_handler(payment_method_id, pay, balance, bank='MTS')

	elif 'Поступление' in sms and 'по СБП' in sms:
		temp = r'Поступление (.*) RUR по СБП от (.*)'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(1).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		balance = -1
		notification_handler(payment_method_id, pay, balance, bank='Alfa')

	elif 'Perevod SBP' in sms:
		temp = r'Perevod SBP ot (.*) iz (.*). Summa (.*) RUR na schet (.*). Ispolnen (.*)'
		payment_result = re.search(temp, sms)

		pay = float(payment_result.group(3).replace(' ', '').replace(',', '.').replace('\xa0', ''))
		balance = -1
		notification_handler(payment_method_id, pay, balance, bank='Uralsib')

	else:
		admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)
		mess = f'❗️НЕИЗВЕСТНОЕ СМС❗️\n{sms}'
		bot.send_message(admin, mess)

	return HttpResponse('ok')

@csrf_exempt
def wallet_callback(request):
    data = json.loads(request.body.decode('utf-8'))
    logger_notifications.info(data)

    try:
        crypt = CryptSettings.objects.get(name=data['coin'].replace('-TRC20', ''))
        confirmations = wallets[crypt.name].get_transaction(data['id'], wallets=True)['confirmations']

        if confirmations >= 1:
            qs = Wallet.objects.filter(crypt=crypt, address=data['address'])

            if qs.exists():
                wallet = qs.first()
                transaction, created = WalletTransaction.objects.get_or_create(
                    wallet=wallet,
                    tx_id=data['id'],
                    defaults={
                        'wallet': wallet,
                        'category': 'deposit',
                        'tx_id': data['id'],
                        'explorer_link': data['explorer_link'],
                        'address': data['address'],
                        'amount': Decimal(data['amount']),
                        'commission': Decimal('0'),
                        'provider_commission': Decimal(data['commission'])
                    }
                )

                if created:
                    wallet.update_balance(transaction.amount - transaction.full_commission)

                    try:
                        template = main_bot.get_template(client_messages.success_deposit_message)
                        mess = template.render(transaction=transaction)
                        main_bot.send_message(wallet.client, mess)

                    except:
                        pass

    except:
        logger_notifications.error({'wallet_callback_error': traceback.format_exc()})
        return HttpResponse(status=403)

    return HttpResponse(status=200)






