from . import messages, keyboards
from telegram.models import Promocode, WithdrawalRequest
import telebot
from general_settings.models import GeneralSettings
import random, string
from django.utils.timezone import datetime
from datetime import timedelta
from wallets import BTCWallet, LTCWallet, XMRWallet, USDTWallet
from . import start as main_menu

static_path = 'telegram/static/img/'
wallets = {
    'BTC': BTCWallet.Wallet,
    'LTC': LTCWallet.Wallet,
    'XMR': XMRWallet.Wallet,
    'USDT': USDTWallet.Wallet
}

def start(bot, client):
    bot_username = bot.get_me().username
    ref_link = f'https://telegram.me/{bot_username}?start={client.tg_id}'

    template = bot.get_template(messages.office_message)
    mess = template.render(client=client, ref_link=ref_link)
    keyboard = keyboards.office_menu
    bot.send_message(client, mess, reply_markup=keyboard)

def start_promocode(bot, client):
    client.set_state('get_promocode')

    mess = messages.get_promocode_message
    keyboard = keyboards.cancel_button
    bot.send_message(client, mess, reply_markup=keyboard)

def get_promocode(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return start(bot, client)

    try:
        promocode = Promocode.objects.get(name=message.text)
        if promocode.one_off and promocode.count >= 1:
            raise Exception()
        if not promocode.available:
            raise Exception()
        
        if promocode.expiration_date and promocode.expiration_date < datetime.now():
            mess = messages.expiration_promocode_message
            bot.send_message(client, mess)
            return
        
        if promocode.used_treshold_value != None and client.count < promocode.used_treshold_value:
            template = bot.get_template(messages.min_promocode_treshold_value)
            mess = template.render(order_count=promocode.used_treshold_value)
            bot.send_message(client, mess)
            return
        
        if promocode.max_used_value != None and promocode.count >= promocode.max_used_value:
            mess = messages.max_used_promocode_message
            bot.send_message(client, mess)
            return
    except:
        mess = messages.incorrect_promocode_message
        bot.send_message(client, mess)
        return

    old_promocodes = client.get_old_promocodes()
    active_promocodes = client.get_active_promocodes()

    if promocode.name in old_promocodes + active_promocodes:
        mess = messages.promocode_already_used_message
        bot.send_message(client, mess)
        return

    promocode.count += 1
    if promocode.one_off:
        promocode.activated_time = datetime.now()
    promocode.save()

    active_promocodes.append(promocode.name)
    client.active_promocodes = ';'.join(active_promocodes)
    client.save()

    client.clear_state()
    template = bot.get_template(messages.activate_promocode_message)
    mess = template.render(promo=promocode)
    keyboard = keyboards.start_menu
    bot.send_message(client, mess, reply_markup=keyboard)

def create_withdrawal(bot, client):
    settings = GeneralSettings.objects.first()
    if client.ref_profit < settings.min_ref_withdrawal:
        template = bot.get_template(messages.not_enough_ref_profit_message)
        mess = template.render(min_ref_withdrawal=settings.min_ref_withdrawal, ref_profit=client.ref_profit)
        keyboard = keyboards.office_menu
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    client.set_state('accept_withdrawal')

    template = bot.get_template(messages.accept_withdrawal_message)
    mess = template.render(client=client)
    keyboard = keyboards.accept_withdrawal_keyboard
    bot.send_message(client, mess, reply_markup=keyboard)

def accept_withdrawal(bot, client, message):
    if message.text == '✅ Да':
        client.clear_state()

        settings = GeneralSettings.objects.first()
        withdrawal = WithdrawalRequest.objects.create(
            requests_id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for i in range(12)),
            client=client,
            summ=client.ref_profit,
            datetime=datetime.now()
        )
        client.ref_profit = 0
        client.save()

        template = bot.get_template(messages.create_withdrawal_message)
        mess = template.render(withdrawal=withdrawal, settings=settings)
        keyboard = keyboards.office_menu
        bot.send_message(client, mess, reply_markup=keyboard)

    elif message.text == '❌ Нет':
        client.clear_state()
        return start(bot, client)

    else:
        bot.delete_message(client, message.message_id)

def get_luck(bot, client):
    keyboard = keyboards.office_menu

    if client.spin_time and client.spin_time + timedelta(days=1) > datetime.now():
        mess = messages.time_error_message
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    if client.discount > 0:
        template = bot.get_template(messages.already_have_discount_message)
        mess = template.render(client=client)
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    result = bot.send_dice(client).dice.value

    if result == 64:
        discount = 100

    elif result in (1, 22, 43):
        discount = 50

    else:
        discount = random.randint(1, 40)

    client.discount = discount
    client.spin_time = datetime.now()
    client.save()

    template = bot.get_template(messages.get_luck_message)
    mess = template.render(client=client)
    bot.send_message(client, mess, reply_markup=keyboard)

def start_calculate(bot, client):
    client.set_state('choice_calc_crypt')

    mess = messages.choice_calc_crypt_message
    keyboard = keyboards.choice_calc_crypt_menu
    bot.send_message(client, mess, reply_markup=keyboard)

def choice_calc_crypt(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return main_menu.start(bot, client)

    if message.text not in ['BTC', 'LTC', 'XMR', 'USDT']:
        bot.delete_message(client, message.message_id)
        return

    client.meta['calc_crypt'] = message.text
    client.save()
    client.set_state('get_calc_value')

    template = bot.get_template(messages.get_calc_value_message)
    mess = template.render(crypt=client.meta['calc_crypt'])
    keyboard = keyboards.cancel_button
    bot.send_message(client, mess, reply_markup=keyboard)

def get_calc_value(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return main_menu.start(bot, client)
        
    try:
        rub_value = int(message.text.replace(',', '.'))
        if rub_value <= 0:
            raise Exception()
    except:
        mess = messages.incorrect_value_message
        keyboard = keyboards.cancel_button
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    wallet = wallets[client.meta['calc_crypt']]
    course = wallet.get_course()
    crypt_value = "{:.8f}".format(rub_value/course)

    client.clear_state()
    template = bot.get_template(messages.calc_result_message)
    mess = template.render(
        rub_value=rub_value,
        crypt_value=crypt_value,
        crypt=client.meta['calc_crypt']
    )
    keyboard = keyboards.office_menu
    bot.send_message(client, mess, reply_markup=keyboard)




















