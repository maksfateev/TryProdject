from . import messages, keyboards
from general_settings.models import GeneralSettings, CryptSettings, PaymentMethod, Card
from django.core.paginator import Paginator
from telegram.models import Promocode, Client, Order, WorkingShift, Wallet
import telebot
from wallets import BTCWallet, LTCWallet, XMRWallet, USDTWallet
import random, string
import re
import time
from threading import Thread
from django.utils.timezone import datetime
import logging
from django.core.cache import cache
import requests
from io import BytesIO

from stats.models import IssuedRequisites, IssuedPayValue, CanceledOrder
from trading.models import Order as TradingOrder
from telegram.modules_trading import messages as trading_messages
from telegram.modules_trading import keyboards as trading_keyboards
from telegram import handler

static_path = 'telegram/static/img/'
wallets = {
    'BTC': BTCWallet.Wallet,
    'LTC': LTCWallet.Wallet,
    'XMR': XMRWallet.Wallet,
    'USDT': USDTWallet.Wallet
}
logger = logging.getLogger('BOT')

class ManyDigitsException(Exception):
    pass

class DummyMessage:
    def __init__(self, text):
        self.text = text

def buy_crypt(bot, client):
    if Order.objects.filter(client=client, status='pending').exists():
        bot.send_message(client, '⛔️ Сначала должен завершиться предыдущий обмен', reply_markup=keyboards.start_menu)
        return

    bot.send_message(client, 'Выберите валюту', reply_markup=keyboards.buy_crypt_menu)

def get_count_after_dot(string):
    index = string.index('.') if '.' in string else string.index(',')
    substring = string[index+1:]
    return len(substring)

def choice_promo(bot, client, call):
    if client.state != 'get_value':
        return
    data = call.data.split('-')
    crypt = client.meta['order']['crypt']
    promocode = Promocode.objects.get(id=int(data[1]))
    if promocode.name == client.meta['order']['promocode']:
        client.meta['order']['promocode'] = None
    else:
        client.meta['order']['promocode'] = promocode.name
    client.save()

    keyboard = telebot.types.InlineKeyboardMarkup()

    # Добавление активных промокодов.
    if len(client.get_active_promocodes()) > 0:
        promocodes = []
        for promo in client.get_active_promocodes():
            promocode = Promocode.objects.get(name=promo)
            promocodes.append(promocode)
        paginator = Paginator(promocodes, 2)
        for i in range(1,paginator.num_pages+1):
            buttons = []
            for item in paginator.page(i):
                discount = f'{item.discount}{"₽" if item.in_fiat else "%"}'
                if client.meta['order']['promocode'] == item.name:
                    text = f'🟢 {item.name} ({discount})'
                else:
                    text = f'🔘 {item.name} ({discount})'
                button = telebot.types.InlineKeyboardButton(text=text, callback_data=f'choice_promo-{item.id}')
                buttons.append(button)
            keyboard.row(*buttons)

    client.set_state('get_value')
    template = bot.get_template(messages.get_value_message)
    mess = template.render(crypt=crypt, client=client)
    if client.meta['order']['promocode']:
        bot.answer_callback_query(call.id, f"✅ Вы активировали промокод {client.meta['order']['promocode']}", show_alert=True)
    message_id = call.message.message_id
    bot.edit_message_text(client, message_id, mess, reply_markup=keyboard)

def buy_btc(bot, client):
    client.update_meta()
    crypt = 'BTC'
    crypt_settings = CryptSettings.objects.get(name=crypt)

    if not crypt_settings.available:
        settings = GeneralSettings.objects.first()
        template = bot.get_template(messages.crypt_not_available_message)
        mess = template.render(crypt=crypt)
        keyboard = keyboards.start_menu
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    client.meta['order']['crypt'] = crypt
    client.save()

    keyboard = telebot.types.InlineKeyboardMarkup()
    if len(client.get_active_promocodes()) > 0:
        promocodes = []
        promocode_names = []
        for promo in client.get_active_promocodes():
            promocode = Promocode.objects.get(name=promo)
            if promocode.expiration_date and datetime.now() > promocode.expiration_date:
                continue
            promocodes.append(promocode)
            promocode_names.append(promocode.name)
        
        client.active_promocodes = ';'.join(promocode_names)
        client.save()

        paginator = Paginator(promocodes, 2)
        for i in range(1,paginator.num_pages+1):
            buttons = []
            for item in paginator.page(i):
                discount = f'{item.discount}{"₽" if item.in_fiat else "%"}'
                if client.meta['order']['promocode'] == item.name:
                    text = f'🟢 {item.name} ({discount})'
                else:
                    text = f'🔘 {item.name} ({discount})'
                button = telebot.types.InlineKeyboardButton(text=text, callback_data=f'choice_promo-{item.id}')
                buttons.append(button)
            keyboard.row(*buttons)


    client.set_state('get_value')
    template = bot.get_template(messages.get_value_message)
    mess = template.render(crypt=crypt, client=client)
    bot.send_message(client, mess, reply_markup=keyboard)
    bot.send_message(client, 'Например: <b>0.00041</b> или <b>1000</b>', reply_markup=keyboards.cancel_button)

def buy_ltc(bot, client):
    client.update_meta()
    crypt = 'LTC'
    crypt_settings = CryptSettings.objects.get(name=crypt)

    if not crypt_settings.available:
        settings = GeneralSettings.objects.first()
        template = bot.get_template(messages.crypt_not_available_message)
        mess = template.render(crypt=crypt)
        keyboard = keyboards.start_menu
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    client.meta['order']['crypt'] = crypt
    client.save()

    keyboard = telebot.types.InlineKeyboardMarkup()
    if len(client.get_active_promocodes()) > 0:
        promocodes = []
        promocode_names = []
        for promo in client.get_active_promocodes():
            promocode = Promocode.objects.get(name=promo)
            if promocode.expiration_date and datetime.now() > promocode.expiration_date:
                continue
            promocodes.append(promocode)
            promocode_names.append(promocode.name)
        
        client.active_promocodes = ';'.join(promocode_names)
        client.save()

        paginator = Paginator(promocodes, 2)
        for i in range(1,paginator.num_pages+1):
            buttons = []
            for item in paginator.page(i):
                discount = f'{item.discount}{"₽" if item.in_fiat else "%"}'
                if client.meta['order']['promocode'] == item.name:
                    text = f'🟢 {item.name} ({discount})'
                else:
                    text = f'🔘 {item.name} ({discount})'
                button = telebot.types.InlineKeyboardButton(text=text, callback_data=f'choice_promo-{item.id}')
                buttons.append(button)
            keyboard.row(*buttons)

    client.set_state('get_value')
    template = bot.get_template(messages.get_value_message)
    mess = template.render(crypt=crypt, client=client)
    bot.send_message(client, mess, reply_markup=keyboard)
    bot.send_message(client, 'Например: <b>0.18</b> или <b>1000</b>', reply_markup=keyboards.cancel_button)

def buy_xmr(bot, client):
    client.update_meta()
    crypt = 'XMR'
    crypt_settings = CryptSettings.objects.get(name=crypt)

    if not crypt_settings.available:
        settings = GeneralSettings.objects.first()
        template = bot.get_template(messages.crypt_not_available_message)
        mess = template.render(crypt=crypt)
        keyboard = keyboards.start_menu
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    client.meta['order']['crypt'] = crypt
    client.save()

    keyboard = telebot.types.InlineKeyboardMarkup()
    if len(client.get_active_promocodes()) > 0:
        promocodes = []
        promocode_names = []
        for promo in client.get_active_promocodes():
            promocode = Promocode.objects.get(name=promo)
            if promocode.expiration_date and datetime.now() > promocode.expiration_date:
                continue
            promocodes.append(promocode)
            promocode_names.append(promocode.name)
        
        client.active_promocodes = ';'.join(promocode_names)
        client.save()

        paginator = Paginator(promocodes, 2)
        for i in range(1,paginator.num_pages+1):
            buttons = []
            for item in paginator.page(i):
                discount = f'{item.discount}{"₽" if item.in_fiat else "%"}'
                if client.meta['order']['promocode'] == item.name:
                    text = f'🟢 {item.name} ({discount})'
                else:
                    text = f'🔘 {item.name} ({discount})'
                button = telebot.types.InlineKeyboardButton(text=text, callback_data=f'choice_promo-{item.id}')
                buttons.append(button)
            keyboard.row(*buttons)

    client.set_state('get_value')
    template = bot.get_template(messages.get_value_message)
    mess = template.render(crypt=crypt, client=client)
    bot.send_message(client, mess, reply_markup=keyboard)
    bot.send_message(client, 'Например: <b>0.065</b> или <b>1000</b>', reply_markup=keyboards.cancel_button)

def buy_usdt(bot, client):
    client.update_meta()
    crypt = 'USDT'
    crypt_settings = CryptSettings.objects.get(name=crypt)

    if not crypt_settings.available:
        settings = GeneralSettings.objects.first()
        template = bot.get_template(messages.crypt_not_available_message)
        mess = template.render(crypt=crypt)
        keyboard = keyboards.start_menu
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    client.meta['order']['crypt'] = crypt
    client.save()

    keyboard = telebot.types.InlineKeyboardMarkup()
    if len(client.get_active_promocodes()) > 0:
        promocodes = []
        promocode_names = []
        for promo in client.get_active_promocodes():
            promocode = Promocode.objects.get(name=promo)
            if promocode.expiration_date and datetime.now() > promocode.expiration_date:
                continue
            promocodes.append(promocode)
            promocode_names.append(promocode.name)
        
        client.active_promocodes = ';'.join(promocode_names)
        client.save()

        paginator = Paginator(promocodes, 2)
        for i in range(1,paginator.num_pages+1):
            buttons = []
            for item in paginator.page(i):
                discount = f'{item.discount}{"₽" if item.in_fiat else "%"}'
                if client.meta['order']['promocode'] == item.name:
                    text = f'🟢 {item.name} ({discount})'
                else:
                    text = f'🔘 {item.name} ({discount})'
                button = telebot.types.InlineKeyboardButton(text=text, callback_data=f'choice_promo-{item.id}')
                buttons.append(button)
            keyboard.row(*buttons)

    client.set_state('get_value')
    template = bot.get_template(messages.get_value_message)
    mess = template.render(crypt=crypt, client=client)
    bot.send_message(client, mess, reply_markup=keyboard)
    bot.send_message(client, 'Например: <b>10</b>', reply_markup=keyboards.cancel_button)

def get_value(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        client.update_deposit_meta()

        settings = GeneralSettings.objects.first()
        template = bot.get_template(messages.start_message)
        mess = template.render(support=settings.support_contact)
        keyboard = keyboards.start_menu

        # image = open(static_path + 'start.jpg', 'rb')
        # bot.send_photo(client, image, caption=mess, reply_markup=keyboard)
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    try:
        enter_value = float(message.text.replace(',', '.'))
        if enter_value <= 0:
            raise Exception()
        if ('.' in message.text or ',' in message.text) and get_count_after_dot(message.text) > 8:
            raise ManyDigitsException()

    except ManyDigitsException:
        mess = messages.many_digits_message
        bot.send_message(client, mess)
        return

    except:
        mess = messages.incorrect_value_message
        bot.send_message(client, mess)
        return

    crypt = client.meta['order']['crypt']
    crypt_settings = CryptSettings.objects.get(name=crypt)
    wallet = wallets[crypt]
    course = wallet.get_course()
    settings = GeneralSettings.objects.first()

    if enter_value >= 15 and crypt != 'USDT':
        rub_value = enter_value
        crypt_value = "{:.8f}".format((rub_value+5)/course)

    elif enter_value >= 600 and crypt == 'USDT':
        rub_value = enter_value
        crypt_value = "{:.2f}".format((rub_value+5)/course)
        
    else:
        crypt_value = enter_value
        rub_value = round(float(crypt_value) * course)

    if rub_value >= 50000:
        client.clear_state()
        client.update_deposit_meta()
        template = bot.get_template(messages.buy_many_crypt_message)
        mess = template.render(support=settings.support_contact)
        keyboard = keyboards.start_menu
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    if client.count == 0 and rub_value < settings.min_value_first:
        client.update_deposit_meta()
        template = bot.get_template(messages.min_value_message)
        mess = template.render(
            rub_value=settings.min_value_first,
            crypt_value="{:.8f}".format(settings.min_value_first/course),
            crypt=crypt,
            support=GeneralSettings.objects.first().support_contact,
        )
        bot.send_message(client, mess)
        return

    if rub_value < crypt_settings.min_value:
        client.update_deposit_meta()
        min_value = crypt_settings.min_value
        template = bot.get_template(messages.min_value_message)
        mess = template.render(
            rub_value=min_value,
            crypt_value="{:.8f}".format(min_value/course),
            crypt=crypt,
            support=GeneralSettings.objects.first().support_contact,
        )
        bot.send_message(client, mess)
        return

    payment_method = PaymentMethod.objects.first()
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton(text=payment_method.card_name, callback_data=f'payment_method-card'),
        telebot.types.InlineKeyboardButton(text=payment_method.sbp_name, callback_data=f'payment_method-sbp'),
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton(text=payment_method.alfa_monobank_name, callback_data=f'payment_method-alfa_monobank')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton(text=payment_method.sber_monobank_name, callback_data=f'payment_method-sber_monobank')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton(text=payment_method.ozon_monobank_name, callback_data=f'payment_method-ozon_monobank')
    )
    # keyboard.row(
    #     telebot.types.InlineKeyboardButton(text=payment_method.add_method_name, callback_data=f'payment_method-add_method')
    # )

    percent = crypt_settings.get_percent(rub_value)
    client.meta['order']['cashback'] = 0
    client.meta['order']['discount'] = 0
    client.meta['order']['crypt_value'] = crypt_value
    client.meta['order']['course'] = course
    client.meta['order']['rub_value'] = rub_value

    if 'deposit_order' in client.meta.keys():
        if rub_value > crypt_settings.threshold_value:
            client.meta['order']['pay_value'] = round(rub_value * (1.0 + (percent/100)))
        else:
            client.meta['order']['pay_value'] = round(rub_value + crypt_settings.fix_comission)
    else:
        if rub_value > crypt_settings.threshold_value:
            client.meta['order']['pay_value'] = round(rub_value * (1.0 + (percent/100))) + crypt_settings.get_comission(course)
        else:
            client.meta['order']['pay_value'] = round(rub_value + crypt_settings.fix_comission + crypt_settings.get_comission())
    client.meta['order']['pay_value'] += random.randint(-10, 10)
    client.meta['order']['real_pay_value'] = client.meta['order']['pay_value']

    if (client.count + 1) % settings.cashback_order_count == 0:
        client.meta['order']['bonus'] = True
        client.meta['order']['discount'] += settings.cashback_order_amount
        client.meta['order']['pay_value'] -= settings.cashback_order_amount
        client.meta['order']['comission_discount'] = settings.cashback_order_amount

        # if rub_value <= 3500 and crypt != 'BTC':
        #     # client.meta['order']['pay_value'] = rub_value + ((client.meta['order']['pay_value'] - rub_value) / 2)
        #     new_pay_value = rub_value + ((client.meta['order']['pay_value'] - rub_value) / 2)
        #     comission_discount = round(client.meta['order']['pay_value'] - new_pay_value)
        #     client.meta['order']['discount'] += comission_discount
        #     client.meta['order']['pay_value'] = new_pay_value
        #     client.meta['order']['comission_discount'] = comission_discount
        # else:
        #     client.meta['order']['discount'] += 200
        #     client.meta['order']['pay_value'] -= 200
        #     client.meta['order']['comission_discount'] = 200
            
    if client.meta['order']['promocode']:
        promocode = Promocode.objects.get(name=client.meta['order']['promocode'])
        if promocode.in_fiat:
            client.meta['order']['pay_value'] -= promocode.discount
            client.meta['order']['discount'] += promocode.discount
            client.meta['order']['promocode_discount'] = promocode.discount
        else:
            profit = client.meta['order']['pay_value'] - client.meta['order']['rub_value']
            client.meta['order']['pay_value'] -= round(profit / 100 * promocode.discount)
            client.meta['order']['discount'] += round(profit / 100 * promocode.discount)
            client.meta['order']['promocode_discount'] = round(profit / 100 * promocode.discount)

    if client.discount > 0:
        client.meta['order']['discount'] += client.discount
        client.meta['order']['pay_value'] -= client.discount

    first_discount = settings.first_discount
    if client.count == 0 and first_discount > 0:
        # profit = client.meta['order']['pay_value'] - client.meta['order']['rub_value']
        # discount = round(profit / 100 * first_discount)
        client.meta['order']['discount'] += settings.first_discount
        client.meta['order']['pay_value'] -= settings.first_discount

    if client.meta['order']['pay_value'] <= 0:
        client.meta['order']['pay_value'] = 10

    if client.meta['order']['pay_value'] % 10 == 0:
        client.meta['order']['pay_value'] += random.randint(1, 5)

    client.meta['order']['exchange_course'] = round(client.meta['order']['pay_value']/float(client.meta['order']['crypt_value']))
    client.meta['order']['pay_value'] = round(client.meta['order']['pay_value'])

    left_count = settings.cashback_order_count - (client.count% settings.cashback_order_count) - 1

    # Stats.
    IssuedPayValue.objects.create(client=client, pay_value=client.meta['order']['pay_value'])

    client.set_state('choice_payment_method')
    template = bot.get_template(messages.choice_payment_method_message)
    mess = template.render(order=client.meta['order'], left_count=left_count, order_count=settings.cashback_order_count, client=client)
    bot.send_message(client, mess, reply_markup=keyboard)

    template = bot.get_template(messages.bonus_order_message)
    mess = template.render(left_count=left_count, order_count=settings.cashback_order_count)
    bot.send_message(client, mess, reply_markup=keyboards.cancel_button)

def activate_cashback(bot, client, call):
    if client.state != 'activate_cashback' or client.meta['order']['cashback'] > 0:
        return

    client.meta['order']['cashback'] = client.cashback
    client.meta['order']['old_pay_value'] = client.meta['order']['pay_value']
    client.meta['order']['pay_value'] -= client.cashback
    if client.meta['order']['pay_value'] <= 0:
        client.meta['order']['pay_value'] = 10
    client.save()

    settings = GeneralSettings.objects.first()
    left_count = settings.cashback_order_count - (client.count% settings.cashback_order_count) - 1

    template = bot.get_template(messages.choice_payment_method_message)
    mess = template.render(order=client.meta['order'], left_count=left_count, order_count=settings.cashback_order_count, client=client)
    activate_cashback_button = telebot.types.InlineKeyboardMarkup()
    activate_cashback_button.row(
            telebot.types.InlineKeyboardButton(text=f'🟢 Да', callback_data=f'activate_cashback'),
            telebot.types.InlineKeyboardButton(text=f'🔘 Нет', callback_data=f'deactivate_cashback'),
    )
    activate_cashback_button.row(
        telebot.types.InlineKeyboardButton(text=f'Далее ➡️', callback_data=f'start_get_address')
    )
    bot.edit_message_text(client, call.message.message_id, mess, reply_markup=activate_cashback_button)

def deactivate_cashback(bot, client, call):
    if client.state != 'activate_cashback' or client.meta['order']['cashback'] == 0:
        return

    client.meta['order']['cashback'] = 0
    client.meta['order']['pay_value'] = client.meta['order']['old_pay_value']
    client.save()

    settings = GeneralSettings.objects.first()
    left_count = settings.cashback_order_count - (client.count% settings.cashback_order_count) - 1

    template = bot.get_template(messages.choice_payment_method_message)
    mess = template.render(order=client.meta['order'], left_count=left_count, order_count=settings.cashback_order_count, client=client)
    activate_cashback_button = telebot.types.InlineKeyboardMarkup()
    activate_cashback_button.row(
            telebot.types.InlineKeyboardButton(text=f'🔘 Да', callback_data=f'activate_cashback'),
            telebot.types.InlineKeyboardButton(text=f'🟢 Нет', callback_data=f'deactivate_cashback'),
    )
    activate_cashback_button.row(
        telebot.types.InlineKeyboardButton(text=f'Далее ➡️', callback_data=f'start_get_address')
    )
    bot.edit_message_text(client, call.message.message_id, mess, reply_markup=activate_cashback_button)

def choice_payment_method(bot, client, message):
    if message.text == '❌ Отмена':
        # Stats.
        canceled_order = CanceledOrder.objects.create(client=client, pay_value=client.meta['order']['pay_value'])

        client.clear_state()
        client.update_deposit_meta()                                                                                                   
        settings = GeneralSettings.objects.first()
        template = bot.get_template(messages.start_message)
        mess = template.render(support=settings.support_contact)
        keyboard = keyboards.start_menu

        # image = open(static_path + 'start.jpg', 'rb')
        # bot.send_photo(client, image, caption=mess, reply_markup=keyboard)
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    bot.delete_message(client, message.message_id)

def get_payment_method(bot, client, call):
    if client.state != 'choice_payment_method':
        return

    data = call.data.split('-')
    payment_type = data[1]
    payment_method = PaymentMethod.objects.first()

    match payment_type:
        case 'card':
            if not payment_method.card_on:
                bot.answer_callback_query(call.id, '❌ Данный метод оплаты недоступен. Выберите другой!', show_alert=True)
                return
            client.meta['order']['payment_method_name'] = payment_method.card_name
        case 'sbp':
            if not payment_method.sbp_on:
                bot.answer_callback_query(call.id, '❌ Данный метод оплаты недоступен. Выберите другой!', show_alert=True)
                return
            client.meta['order']['payment_method_name'] = payment_method.sbp_name
        case 'add_method':
            if not payment_method.add_method_on:
                bot.answer_callback_query(call.id, '❌ Данный метод оплаты недоступен. Выберите другой!', show_alert=True)
                return
            client.meta['order']['payment_method_name'] = payment_method.add_method_name
        case 'alfa_monobank':
            if not payment_method.alfa_monobank_on:
                bot.answer_callback_query(call.id, '❌ Данный метод оплаты недоступен. Выберите другой!', show_alert=True)
                return
            client.meta['order']['payment_method_name'] = payment_method.alfa_monobank_name
        case 'sber_monobank':
            if not payment_method.sber_monobank_on:
                bot.answer_callback_query(call.id, '❌ Данный метод оплаты недоступен. Выберите другой!', show_alert=True)
                return
            client.meta['order']['payment_method_name'] = payment_method.sber_monobank_name
        case 'ozon_monobank':
            if not payment_method.ozon_monobank_on:
                bot.answer_callback_query(call.id, '❌ Данный метод оплаты недоступен. Выберите другой!', show_alert=True)
                return
            client.meta['order']['payment_method_name'] = payment_method.ozon_monobank_name

    client.meta['order']['payment_type'] = payment_type
        
    # client.meta['order']['requisites'] = payment_method.card_number if payment_type == 'card' else payment_method.sbp_number
    client.save()

    settings = GeneralSettings.objects.first()
    left_count = settings.cashback_order_count - (client.count% settings.cashback_order_count) - 1
    template = bot.get_template(messages.choice_payment_method_message)
    mess = template.render(order=client.meta['order'], client=client, left_count=left_count, order_count=settings.cashback_order_count,)
    bot.edit_message_text(client, call.message.message_id, mess, reply_markup=None)

    if 'deposit_order' in client.meta.keys():
        crypt = CryptSettings.objects.get(name=client.meta['order']['crypt'])
        if not Wallet.objects.filter(crypt=crypt, client=client).exists():
            client.clear_state()
            client.update_deposit_meta()
            mess = f'❌ Создайте внутренний {crypt} адресс, и попробуйте пополнить снова!'
            keyboard = keyboards.start_menu

            bot.send_message(client, mess, reply_markup=keyboard)
            return
        
        wallet = Wallet.objects.get(crypt=crypt, client=client)

        if payment_type in ['alfa_monobank', 'sber_monobank', 'ozon_monobank']:
            client.meta['order']['is_dummy'] = True
            client.save()

            client.set_state('accept_monobank')

            if payment_type == 'alfa_monobank':
                bot.send_message(client, payment_method.alfa_monobank_description, reply_markup=keyboards.accept_monobank_keyboard)
            elif payment_type == 'ozon_monobank':
                bot.send_message(client, payment_method.ozon_monobank_description, reply_markup=keyboards.accept_monobank_keyboard)
            else:
                bot.send_message(client, payment_method.sber_monobank_description, reply_markup=keyboards.accept_monobank_keyboard)

        else:
            dummy_message = DummyMessage(wallet.address)
            get_address(bot, client, dummy_message)

    else:
        if payment_type in ['alfa_monobank', 'sber_monobank', 'ozon_monobank']:
            client.set_state('accept_monobank')

            if payment_type == 'alfa_monobank':
                bot.send_message(client, payment_method.alfa_monobank_description, reply_markup=keyboards.accept_monobank_keyboard)
            elif payment_type == 'ozon_monobank':
                bot.send_message(client, payment_method.ozon_monobank_description, reply_markup=keyboards.accept_monobank_keyboard)
            else:
                bot.send_message(client, payment_method.sber_monobank_description, reply_markup=keyboards.accept_monobank_keyboard)

        else:
            client.set_state('get_address')
            crypt = client.meta['order']['crypt']
            template = bot.get_template(messages.get_address_message)
            mess = template.render(crypt=crypt)
            bot.send_message(client, mess, reply_markup=keyboards.cancel_button)

    # settings = GeneralSettings.objects.first()
    # left_count = settings.cashback_order_count - (client.count% settings.cashback_order_count) - 1

    # client.set_state('activate_cashback')
    # template = bot.get_template(messages.choice_payment_method_message)
    # mess = template.render(order=client.meta['order'], client=client, left_count=left_count, order_count=settings.cashback_order_count)
    # activate_cashback_button = telebot.types.InlineKeyboardMarkup()
    # if client.cashback > 0 and not client.meta['order']['bonus']:
    #     activate_cashback_button.row(
    #         telebot.types.InlineKeyboardButton(text=f'🔘 Да', callback_data=f'activate_cashback'),
    #         telebot.types.InlineKeyboardButton(text=f'🟢 Нет', callback_data=f'deactivate_cashback'),
    #     )
    # activate_cashback_button.row(
    #     telebot.types.InlineKeyboardButton(text=f'Далее ➡️', callback_data=f'start_get_address')
    # )
    # bot.edit_message_text(client, call.message.message_id, mess, reply_markup=activate_cashback_button)


def accept_monobank(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        client.update_deposit_meta()

        settings = GeneralSettings.objects.first()
        template = bot.get_template(messages.start_message)
        mess = template.render(support=settings.support_contact)
        keyboard = keyboards.start_menu
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    if message.text == 'Я понимаю':
        if client.meta['order'].get('is_dummy', False) == True:
            crypt = CryptSettings.objects.get(name=client.meta['order']['crypt'])
            wallet = Wallet.objects.get(crypt=crypt, client=client)
            dummy_message = DummyMessage(wallet.address)
            get_address(bot, client, dummy_message)
        
        else:
            client.set_state('get_address')
            crypt = client.meta['order']['crypt']
            template = bot.get_template(messages.get_address_message)
            mess = template.render(crypt=crypt)
            bot.send_message(client, mess, reply_markup=keyboards.cancel_button)
    

def activate_cashback_message(bot, client, message):
    if message.text == '❌ Отмена':
        # Stats.
        canceled_order = CanceledOrder.objects.create(client=client, pay_value=client.meta['order']['pay_value'])

        client.clear_state()
        client.update_deposit_meta()
        settings = GeneralSettings.objects.first()
        template = bot.get_template(messages.start_message)
        mess = template.render(support=settings.support_contact)
        keyboard = keyboards.start_menu

        # image = open(static_path + 'start.jpg', 'rb')
        # bot.send_photo(client, image, caption=mess, reply_markup=keyboard)
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    bot.delete_message(client, message.message_id)

def start_get_address(bot, client, call):
    if client.state != 'choice_payment_method':
        return

    client.set_state('get_address')

    settings = GeneralSettings.objects.first()
    left_count = settings.cashback_order_count - (client.count% settings.cashback_order_count) - 1
    template = bot.get_template(messages.choice_payment_method_message)
    mess = template.render(order=client.meta['order'], client=client, left_count=left_count, order_count=settings.cashback_order_count,)
    bot.edit_message_text(client, call.message.message_id, mess, reply_markup=None)

    crypt = client.meta['order']['crypt']
    template = bot.get_template(messages.get_address_message)
    mess = template.render(crypt=crypt)
    bot.send_message(client, mess, reply_markup=keyboards.cancel_button)

def get_address(bot, client, message):
    if message.text == '❌ Отмена':
        # Stats.
        canceled_order = CanceledOrder.objects.create(client=client, pay_value=client.meta['order']['pay_value'])

        client.clear_state()
        client.update_deposit_meta()
        settings = GeneralSettings.objects.first()
        template = bot.get_template(messages.start_message)
        mess = template.render(support=settings.support_contact)
        keyboard = keyboards.start_menu

        # image = open(static_path + 'start.jpg', 'rb')
        # bot.send_photo(client, image, caption=mess, reply_markup=keyboard)
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    crypt = client.meta['order']['crypt']
    wallet = wallets[crypt]
    search_result = re.search(wallet.address_regex, message.text)
    if not search_result:
        template = bot.get_template(messages.incorrect_address_message)
        mess = template.render(crypt=crypt)
        bot.send_message(client, mess)
        return

    client.meta['order']['address'] = message.text
    client.save()

    # Stats.
    IssuedRequisites.objects.create(client=client, pay_value=client.meta['order']['pay_value'])

    payment_method = PaymentMethod.objects.first()
    bot.send_message(client, '⏳ Идет подбор реквизитов', reply_markup=keyboards.cancel_button)

    try:
        payment_data = payment_method.get_requisites(
            client.meta['order']['pay_value'],
            client.meta['order']['payment_type']
        )

    except (payment_method.GetRequisitesTimeOut, payment_method.GetRequisitesException):
        payment_data = None

        if payment_data is None:

            if client.meta['order']['payment_type'] == 'alfa_monobank':
                bot.send_message(
                    client,
                    '❗️По методу АЛЬФА - АЛЬФА не нашлось реквизитов. Вы можете переводить с любого удобного банка.',
                    reply_markup=keyboards.cancel_button
                )
                payment_types = ['sbp']

            elif client.meta['order']['payment_type'] == 'sber_monobank':
                bot.send_message(
                    client,
                    '❗️По методу СБЕР - СБЕР не нашлось реквизитов. Вы можете переводить с любого удобного банка.',
                    reply_markup=keyboards.cancel_button
                )
                payment_types = ['sbp']
            
            elif client.meta['order']['payment_type'] == 'ozon_monobank':
                bot.send_message(
                    client,
                    '❗️По методу ОЗОН - ОЗОН не нашлось реквизитов. Вы можете переводить с любого удобного банка.',
                    reply_markup=keyboards.cancel_button
                )
                payment_types = ['sbp']

            if client.meta['order']['payment_type'] == 'card':
                payment_types = ['sbp']

            if client.meta['order']['payment_type'] == 'sbp':
                payment_types = ['card']

            # if client.meta['order']['payment_type'] == 'add_method':
            #     payment_types = ['sbp', 'card']

            bot.send_message(
                client,
                '❗️⏳ Подбор реквизитов идет дольше обычного, пожалуйста ожидайте!',
                reply_markup=keyboards.cancel_button
            )

            for payment_type in payment_types:
                try:
                    payment_data = payment_method.get_requisites(
                        client.meta['order']['pay_value'],
                        payment_type
                    )
                    client.meta['order']['payment_type'] = payment_type
                    break

                except (payment_method.GetRequisitesTimeOut, payment_method.GetRequisitesException):
                    continue
            
        if payment_data is None:
            logger.warning(f"Не удалось получить реквизиты для {client.meta['order']['pay_value']} {client.meta['order']['payment_type']}")

            bot.send_message(
                client,
                '❌ Что-то пошло не так. Попробуйте сделать обмен на сумму от 10000р. Это гарантирует <u>быструю выдачу реквизитов</u> и <u>меньшую комиссию</u>!',
                reply_markup=keyboards.cancel_button
            )
            return

    kwargs = {}

    if 'link' in payment_data:
        client.meta['order']['pay_link'] = payment_data['link']
        client.meta['order']['requisites'] = 'Платежная ссылка'

        template = bot.get_template(messages.order_info_message_with_pay_link)
        kwargs['pay_link'] = payment_data['link']

    else:
        client.meta['order']['payment_method_name'] = payment_data['bank'] or client.meta['order']['payment_method_name']
        client.meta['order']['requisites'] = payment_data['reqs']

        template = bot.get_template(messages.order_info_message)

    if 'payok_id' in payment_data:
        client.meta['order']['payok_id'] = payment_data['payok_id']

    client.meta['order']['provider'] = payment_data['provider']

    if payment_data['provider'] == 'macrodroid':
        client.meta['order']['card_id'] = payment_data['label']
        client.meta['order']['label'] = None
    else:
        client.meta['order']['label'] = payment_data['label']

    client.save()

    settings = GeneralSettings.objects.first()
    client.set_state('choice_action')

    mess = template.render(order=client.meta['order'], timer=settings.time_for_payment, **kwargs)
    keyboard = keyboards.order_menu
    m = bot.send_message(client, mess, reply_markup=keyboard)

    if client.meta['order']['payment_type'] == 'card':
        bot.send_message(client, '<b>' + payment_method.card_description + '</b>', reply_markup=telebot.types.ReplyKeyboardRemove())

    elif client.meta['order']['payment_type'] == 'sbp':
        bot.send_message(client, '<b>' + payment_method.sbp_description + '</b>', reply_markup=telebot.types.ReplyKeyboardRemove())
    
    elif client.meta['order']['payment_type'] == 'alfa_monobank':
        bot.send_message(client, '<b>' + payment_method.alfa_monobank_description + '</b>', reply_markup=telebot.types.ReplyKeyboardRemove())

    elif client.meta['order']['payment_type'] == 'sber_monobank':
        bot.send_message(client, '<b>' + payment_method.sber_monobank_description + '</b>', reply_markup=telebot.types.ReplyKeyboardRemove())
    
    elif client.meta['order']['payment_type'] == 'ozon_monobank':
        bot.send_message(client, '<b>' + payment_method.ozon_monobank_description + '</b>', reply_markup=telebot.types.ReplyKeyboardRemove())

    else:
        bot.send_message(client, '<b>' + payment_method.add_method_description + '</b>', reply_markup=telebot.types.ReplyKeyboardRemove())

    thread = Thread(target=wait_for_payment, args=(bot, client, m.message_id, client.meta['order'], settings.time_for_payment, template, kwargs))
    thread.start()

def wait_for_payment(bot, client, message_id, order, timer, template, kwargs):
    tg_id = client.tg_id
    while timer != 0:
        time.sleep(60)
        client = Client.objects.get(tg_id=tg_id)
        if client.meta['order'] != order:
            print('break')
            return

        timer -= 1
        mess = template.render(order=order, timer=timer, **kwargs)
        keyboard = keyboards.order_menu
        try:
            bot.edit_message_text(client, message_id, mess, reply_markup=keyboard)
        except Exception as e:
            print(e)
            return

    client.clear_state()
    client.update_deposit_meta()
    client.update_meta()

    mess = template.render(order=order)
    bot.edit_message_text(client, message_id, mess)

    mess = messages.cancel_order_message
    bot.send_message(client, mess, reply_markup=keyboards.start_menu)


def choice_action(bot, client, message):
    bot.delete_message(client, message.message_id)

def cancel_order(bot, client, call):
    # Stats.
    canceled_order = CanceledOrder.objects.create(client=client, pay_value=client.meta['order']['pay_value'])
    
    template = bot.get_template(messages.order_info_message)
    mess = template.render(order=client.meta['order'])
    bot.edit_message_text(client, call.message.message_id, mess)

    client.clear_state()
    client.update_meta()
    client.update_deposit_meta()

    mess = messages.cancel_order_message
    bot.send_message(client, mess, reply_markup=keyboards.start_menu)

def accept_pay(bot, client, call):
    if client.meta['order']['promocode'] is not None and client.meta['order']['promocode'] not in client.get_active_promocodes():
        client.clear_state()
        client.update_meta()

        bot.edit_message_reply_markup(client, call.message.message_id, None)
        bot.send_message(client, '⛔️ Что-то пошло не так. Попробуйте еще раз', reply_markup=keyboards.start_menu)
        return
    
    discount_info = {
        'bonus_discount': client.meta['order'].get('comission_discount', None) if client.meta['order'].get('comission_discount', None) else 0,
        'cashback': client.meta['order']['cashback'],
        'lucky': client.discount,
        'promocode': client.meta['order'].get('promocode_discount', None) if client.meta['order'].get('promocode_discount', None) else 0,
    }
    all_discount = discount_info['bonus_discount'] + discount_info['cashback'] + discount_info['lucky'] + discount_info['promocode']

    order = Order.objects.create(
        working_shift=WorkingShift.current(),
        order_id=''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for i in range(18)),
        client=client,
        crypt=client.meta['order']['crypt'],
        crypt_value=client.meta['order']['crypt_value'],
        course=client.meta['order']['course'],
        rub_value=client.meta['order']['rub_value'],
        pay_value=client.meta['order']['pay_value'],
        address=client.meta['order']['address'],
        payment_method=client.meta['order']['payment_method_name'],
        requisites=client.meta['order']['requisites'],
        datetime=datetime.now(),
        discount=all_discount,
        cashback=client.meta['order']['cashback'],
        promocode=client.meta['order']['promocode'],
        provider=client.meta['order']['provider'],
        label=client.meta['order']['label'],
        discount_info=discount_info
    )

    if order.provider == 'macrodroid' and 'card_id' in client.meta['order'].keys():
        order.payload['card_id'] = client.meta['order']['card_id']
        order.save()

    if 'payok_id' in client.meta['order']:
        order.payload['payok_id'] = client.meta['order']['payok_id']
        order.save()

    if client.meta['order']['bonus']:
        order.bonus_order = True
        order.save()

    settings = GeneralSettings.objects.first()

    try:
        bot.edit_message_reply_markup(client, call.message.message_id, None)

        template = bot.get_template(messages.wait_message)
        mess = template.render(order=order)
        keyboard = keyboards.get_paychek_menu(order_id=order.order_id)
        wait_message = bot.send_message(client, mess, reply_markup=keyboard)
    except:
        order.delete()
        return error_accept_pay(bot, client, call)

    if order.promocode:
        request_obj = Promocode.objects.filter(name=order.promocode).first()
        promocodes = client.get_active_promocodes()
        try:
            if request_obj is not None and request_obj.one_off:
                request_obj.used_time = datetime.now()
                request_obj.client_used = client
                request_obj.save()
            promocodes.remove(order.promocode)
        except:
            pass
        client.active_promocodes = ';'.join(promocodes)
        client.save()

    if client.discount > 0:
        client.discount = 0
        client.save()

    admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)

    template = bot.get_template(messages.order_message)
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
    
    cache.set(
        f'order_{order.id}',
        {'message': mess, 'has_keyboard': has_keyboard},
        settings.time_for_order * 60
    )
    try:
        match order.crypt:
            case 'BTC':
                m = handler.btc_bot.send_message(admin, mess, reply_markup=keyboard)

            case 'LTC':
                m = handler.ltc_bot.send_message(admin, mess, reply_markup=keyboard)

            case 'XMR':
                m = handler.xmr_bot.send_message(admin, mess, reply_markup=keyboard)

            case 'USDT':
                m = handler.usdt_bot.send_message(admin, mess, reply_markup=keyboard)

        order.message_id = m.message_id
        order.save()
        client.clear_state()
        client.update_meta()
        client.update_deposit_meta()

        if order.provider == 'macrodroid':
            card = Card.objects.get(id=int(order.payload['card_id']))

            if card.trader is not None:
                trading_order = TradingOrder.objects.create(
                    order_id=order.order_id,
                    trader=card.trader,
                    amount=int(order.pay_value),
                    bank=card.bank,
                    cardholder_name=card.cardholder_name,
                    requisites=order.requisites
                )

                template = bot.get_template(trading_messages.order_message)
                mess = template.render(order=trading_order)
                keyboard = trading_keyboards.get_order_keyboard(trading_order)

                handler.trading_bot.send_message(trading_order.trader.client, mess, reply_markup=keyboard)

    except Exception as e:
        logger.error(e)
        bot.delete_message(client, wait_message.message_id)
        order.delete()
        return error_accept_pay(bot, client, call)

def error_accept_pay(bot, client, call):
    keyboard = keyboards.order_menu
    try:
        bot.edit_message_reply_markup(client, call.message.message_id, keyboard)
    except:
        pass
    bot.answer_callback_query(call.id, f'⛔️ Ошибка при отправке заявки, попробуйте еще раз', show_alert=True)


def start_paychek(bot, client, call):
    bot.edit_message_reply_markup(client, call.message.message_id, None)
    order_id = call.data.split('-')[1]

    client.meta['order']['id'] = order_id
    client.meta['order']['message_id'] = call.message.message_id
    client.save()

    client.set_state('get_paycheck')
    bot.send_message(client, f'📎 Отправьте PDF или фото чека оплаты по заявке {order_id}', reply_markup=keyboards.cancel_button)


def cancel_paychek(bot, client, call):
    bot.edit_message_reply_markup(client, call.message.message_id, None)


def get_paycheck(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        client.update_meta()

        settings = GeneralSettings.objects.first()
        template = bot.get_template(messages.start_message)
        mess = template.render(support=settings.support_contact)
        keyboard = keyboards.start_menu

        bot.send_message(client, mess, reply_markup=keyboard)
        return
    
    try:
        order = Order.objects.get(order_id=client.meta['order']['id'])
        admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)

        bot_map = {
            'BTC': handler.btc_bot,
            'LTC': handler.ltc_bot,
            'XMR': handler.xmr_bot,
            'USDT': handler.usdt_bot
        }
        target_bot = bot_map.get(order.crypt)

        if not target_bot:
            bot.send_message(client, "⛔️ Неизвестная валюта.")
            return

        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            file_data = requests.get(f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}").content
            file_obj = BytesIO(file_data)
            file_obj.name = "check.jpg"
            target_bot.send_photo(admin, file_obj, caption=f"📄 Чек оплаты {order.order_id}")

        elif message.content_type == 'document':
            file_id = message.document.file_id
            file_info = bot.get_file(file_id)
            file_data = requests.get(f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}").content
            file_obj = BytesIO(file_data)
            file_obj.name = message.document.file_name or "check.pdf"
            target_bot.send_document(admin, file_obj, caption="📄 Чек оплаты", reply_to_message_id=order.message_id)

        else:
            bot.send_message(client, "⛔️ Пришлите фото или PDF чека.")
            return

        client.clear_state()
        client.update_meta()
        bot.send_message(client, "✅ Чек успешно отправлен", reply_markup=keyboards.start_menu)

    except Exception as e:
        logger.error(e)
        client.clear_state()
        client.update_meta()
        bot.send_message(client, "❌ Ошибка при отправке", reply_markup=keyboards.start_menu)





