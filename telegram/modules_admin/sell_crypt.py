from . import messages, keyboards
from .start import start
from general_settings.models import GeneralSettings, CryptSellSettings, PaymentMethod
from telegram.models import OrderSell, Client
from wallets import BTCWallet, LTCWallet, XMRWallet
import logging
import telebot
import re
import random, string, time
from telegram import handler
from django.utils.timezone import datetime

wallets = {
    'BTC': BTCWallet.Wallet,
    'LTC': LTCWallet.Wallet,
    'XMR': XMRWallet.Wallet,
}
logger = logging.getLogger('BOT')
class ManyDigitsException(Exception):
    pass

def get_count_after_dot(string):
    index = string.index('.') if '.' in string else string.index(',')
    substring = string[index + 1:]
    return len(substring)

def sell_crypt(bot, client):
    bot.send_message(client, 'Выберите валюту', reply_markup=keyboards.sell_crypt_menu)

def sell_btc(bot, client):
    client.update_sell_meta()
    crypt = 'BTC'
    crypt_settings = CryptSellSettings.objects.get(name=crypt)
    if not crypt_settings.available:
        general_settings = GeneralSettings.objects.first()
        template = bot.get_template(messages.sell_crypt_not_available_message)
        mess = template.render(crypt=crypt, settings=general_settings)
        keyboard = keyboards.start_menu
        bot.send_message(client, mess, reply_markup=keyboard)
        return
    client.meta['order_sell']['crypt'] = crypt
    client.save()
    # real_course = wallets[crypt].get_course()
    # course = real_course * (1.0 + (crypt_settings.percent / 100))
    client.set_state('get_client_tg_id')
    mess = messages.get_tg_id_message
    bot.send_message(client, mess, reply_markup=keyboards.cancel_button)

def sell_ltc(bot, client):
    client.update_sell_meta()
    crypt = 'LTC'
    crypt_settings = CryptSellSettings.objects.get(name=crypt)
    if not crypt_settings.available:
        general_settings = GeneralSettings.objects.first()
        template = bot.get_template(messages.sell_crypt_not_available_message)
        mess = template.render(crypt=crypt, settings=general_settings)
        keyboard = keyboards.start_menu
        bot.send_message(client, mess, reply_markup=keyboard)
        return
    client.meta['order_sell']['crypt'] = crypt
    client.save()
    # real_course = wallets[crypt].get_course()
    # course = real_course * (1.0 + (crypt_settings.percent / 100))
    client.set_state('get_client_tg_id')
    mess = messages.get_tg_id_message
    bot.send_message(client, mess, reply_markup=keyboards.cancel_button)

def sell_xmr(bot, client):
    client.update_sell_meta()
    crypt = 'XMR'
    crypt_settings = CryptSellSettings.objects.get(name=crypt)
    if not crypt_settings.available:
        general_settings = GeneralSettings.objects.first()
        template = bot.get_template(messages.sell_crypt_not_available_message)
        mess = template.render(crypt=crypt, settings=general_settings)
        keyboard = keyboards.start_menu
        bot.send_message(client, mess, reply_markup=keyboard)
        return
    client.meta['order_sell']['crypt'] = crypt
    client.save()
    # real_course = wallets[crypt].get_course()
    # course = real_course * (1.0 + (crypt_settings.percent / 100))
    client.set_state('get_client_tg_id')
    mess = messages.get_tg_id_message
    bot.send_message(client, mess, reply_markup=keyboards.cancel_button)

def sell_usdt(bot, client):
    client.update_sell_meta()
    crypt = 'USDT'
    crypt_settings = CryptSellSettings.objects.get(name=crypt)
    if not crypt_settings.available:
        general_settings = GeneralSettings.objects.first()
        template = bot.get_template(messages.sell_crypt_not_available_message)
        mess = template.render(crypt=crypt, settings=general_settings)
        keyboard = keyboards.start_menu
        bot.send_message(client, mess, reply_markup=keyboard)
        return
    client.meta['order_sell']['crypt'] = crypt
    client.save()
    # real_course = wallets[crypt].get_course()
    # course = real_course * (1.0 + (crypt_settings.percent / 100))
    client.set_state('get_client_tg_id')
    mess = messages.get_tg_id_message
    bot.send_message(client, mess, reply_markup=keyboards.cancel_button)

def get_client_tg_id(bot, client, message):
    if message.text == '❌ Отмена':
        return start(bot, client)
    
    if not message.text.isdigit():
        mess = messages.incorrect_tg_id_message
        bot.send_message(client, mess)
        return
    
    client_query = Client.objects.filter(tg_id=int(message.text))
    if not client_query.exists():
        template = bot.get_template(messages.client_not_exist_message)
        mess = template.render(tg_id=message.text)
        bot.send_message(client, mess)
        return
    
    client.meta['order_sell']['client_tg_id'] = message.text
    client.set_state('get_sell_value')
    template = bot.get_template(messages.get_sell_value_message)
    mess = template.render(crypt=client.meta['order_sell']['crypt'])
    bot.send_message(client, mess, reply_markup=keyboards.cancel_button)

def get_value(bot, client, message):
    if message.text == '❌ Отмена':
        return start(bot, client)
    try:
        enter_value = float(message.text.replace(',', '.').replace('\xa0', '').replace(' ', ''))
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
    crypt = client.meta['order_sell']['crypt']
    crypt_settings = CryptSellSettings.objects.get(name=crypt)
    wallet = wallets[crypt]
    course = wallet.get_course()
    # Change later.
    # if enter_value >= 15 and crypt != 'USDT':
    #     template = bot.get_template(messages.sell_crypt_rub_valuer_error)
    #     mess = template.render(
    #         crypt=crypt
    #     )
    #     bot.send_message(client, mess)
    #     return
    # else:
    #     crypt_value = enter_value
    #     rub_value = round(float(crypt_value) * course)
    crypt_value = enter_value
    rub_value = round(float(crypt_value) * course)
    if rub_value < crypt_settings.min_value_sell:
        min_value = crypt_settings.min_value_sell
        template = bot.get_template(messages.min_value_message)
        mess = template.render(
            rub_value=min_value,
            crypt_value="{:.8f}".format(min_value / course),
            crypt=crypt
        )
        bot.send_message(client, mess)
        return
    payment_methods = PaymentMethod.objects.all()
    keyboard = telebot.types.InlineKeyboardMarkup()
    for payment_method in payment_methods:
        card_button = telebot.types.InlineKeyboardButton(
            text=payment_method.card_name,
            callback_data=f'payment_method_sell-card-{payment_method.id}',
            resize_keyboard=True
        )
        sbp_button = telebot.types.InlineKeyboardButton(
            text=payment_method.sbp_name,
            callback_data=f'payment_method_sell-sbp-{payment_method.id}',
            resize_keyboard=True
        )
        # keyboard.row(card_button)
        keyboard.row(sbp_button)
        break
    # Use percent.
    percent = crypt_settings.percent
    client.meta['order_sell']['crypt_value'] = crypt_value
    client.meta['order_sell']['course'] = course
    client.meta['order_sell']['rub_value'] = rub_value
    client.meta['order_sell']['pay_value_with_percent'] = round(rub_value - (rub_value * (percent / 100)))
    client.save()
    # # Stats.
    # IssuedPayValue.objects.create(client=client, pay_value=client.meta['order_sell']['pay_value_with_percent'])
    client.set_state('choice_sell_payment_method')
    template = bot.get_template(messages.choice_sell_payment_method)
    mess = template.render(order_sell=client.meta['order_sell'], crypt=crypt)
    bot.send_message(client, mess, reply_markup=keyboard)
    bot.send_message(client, '-------------------------------------------------', reply_markup=keyboards.cancel_button)

def choice_payment_method(bot, client, message):
    if message.text == '❌ Отмена':
        return start(bot, client)
    bot.delete_message(client, message.message_id)

def get_payment_method(bot, client, call):
    if client.state != 'choice_sell_payment_method':
        return
    bot.delete_message(client, call.message.message_id)
    data = call.data.split('-')
    payment_type = data[1]
    if payment_type == 'sbp':
        template_mess = 'СБП - Номер телефона'
        client.set_state('get_sbp_requisites')
    else:
        template_mess = 'Номер карты'
        client.set_state('get_card_requisites')
    client.meta['order_sell']['payment_method'] = template_mess
    client.save()
    template = bot.get_template(messages.get_requisites_sell_payment_method)
    mess = template.render(payment_type=template_mess)
    bot.send_message(client, mess)

def get_card_requisites(bot, client, message):
    if message.text == '❌ Отмена':
        return start(bot, client)
    card_number = message.text.replace(' ', '')
    if not card_number.isdigit() or len(card_number) != 16:
        bot.send_message(client, messages.sell_crypt_input_card_error)
        return
    crypt = client.meta['order_sell']['crypt']
    client.meta['order_sell']['requisites'] = message.text
    client.save()
    client.set_state('accept_sell')
    template = bot.get_template(messages.sell_order_message)
    mess = template.render(order_sell=client.meta['order_sell'], crypt=crypt, requisites=message.text)
    bot.send_message(client, mess, reply_markup=keyboards.order_sell_menu)

def get_sbp_requisites(bot, client, message):
    if message.text == '❌ Отмена':
        return start(bot, client)
    pattern = re.compile(r'^\+?(\d[\s()-]?){10}\d$')
    if not pattern.match(message.text) is not None:
        bot.send_message(client, messages.sell_crypt_input_sbp_error)
        return
    crypt = client.meta['order_sell']['crypt']
    client.meta['order_sell']['requisites'] = message.text
    client.save()
    client.set_state('get_bank_name')
    template = bot.get_template(messages.order_sell_get_bank_message)
    mess = template.render(crypt=crypt)
    bot.send_message(client, mess, reply_markup=keyboards.cancel_button)

def get_bank_name(bot, client, message):
    if message.text == '❌ Отмена':
        return start(bot, client)
    crypt = client.meta['order_sell']['crypt']
    requisites = f"{client.meta['order_sell']['requisites']} {message.text}"
    client.meta['order_sell']['requisites'] = requisites
    client.save()
    client.set_state('accept_sell')
    template = bot.get_template(messages.sell_order_message)
    mess = template.render(order_sell=client.meta['order_sell'], crypt=crypt, requisites=requisites)
    bot.send_message(client, mess, reply_markup=keyboards.order_sell_menu)

def accept_sell(bot, client, message):
    if message.text == '❌ Отмена':
        return start(bot, client)
    elif message.text == '✅ Продолжить':
        crypt = client.meta['order_sell']['crypt']
        client_tg_id = client.meta['order_sell']['client_tg_id']
        sell_client = Client.objects.filter(tg_id=client_tg_id).get()
        address = wallets[crypt].get_address()
        order_sell = OrderSell.objects.create(
            order_id=''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for i in range(18)),
            client=sell_client,
            crypt=crypt,
            crypt_value=client.meta['order_sell']['crypt_value'],
            course=client.meta['order_sell']['course'],
            rub_value=client.meta['order_sell']['rub_value'],
            pay_value_with_percent=client.meta['order_sell']['pay_value_with_percent'],
            address=address,
            payment_method=client.meta['order_sell']['payment_method'],
            requisites=client.meta['order_sell']['requisites'],
            datetime=datetime.now(),
        )
        general_settings = GeneralSettings.objects.first()
        client.clear_state()
        client.update_sell_meta()
        template = bot.get_template(messages.order_sell_info_message)
        mess = template.render(order_sell=order_sell, time=general_settings.time_for_sell)
        bot.send_message(client, mess, reply_markup=keyboards.start_menu)
    else:
        bot.delete_message(client, message.message_id)
