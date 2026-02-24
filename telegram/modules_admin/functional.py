import datetime

from . import messages, keyboards
import telebot

from telegram.models import Client, Withdrawal, WorkingShift, Operator, Duty

from general_settings.models import CryptSettings, PaymentMethod

from django.core.paginator import Paginator

import re


def start(bot, client):
    mess = messages.start_message
    keyboard = keyboards.functional_menu
    bot.send_message(client, mess, reply_markup=keyboard)

def start_ref_transfer(bot, client):
    client.set_state('get_ref_id')

    mess = 'Введите tg id <b>реферала</b>'
    keyboard = keyboards.cancel_button
    bot.send_message(client, mess, reply_markup=keyboard)

def get_ref_id(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        mess = messages.start_message
        keyboard = keyboards.functional_menu
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    if not message.text.isdigit():
        mess = '❌ Некорректный tg id'
        keyboard = keyboards.cancel_button
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    qs = Client.objects.filter(tg_id=int(message.text))
    if not qs.exists():
        mess = '❌ Такого реферала не существует'
        keyboard = keyboards.cancel_button
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    client.meta['ref_transfer'] = {'ref_id': int(message.text)}
    client.save()
    client.set_state('get_father_id')

    mess = 'Введите tg id <b>рефовода</b>'
    keyboard = keyboards.cancel_button
    bot.send_message(client, mess, reply_markup=keyboard)

def get_father_id(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        mess = messages.start_message
        keyboard = keyboards.functional_menu
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    if not message.text.isdigit():
        mess = '❌ Некорректный tg id'
        keyboard = keyboards.cancel_button
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    qs = Client.objects.filter(tg_id=int(message.text))
    if not qs.exists():
        mess = '❌ Такого рефовода не существует'
        keyboard = keyboards.cancel_button
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    father = qs.first()
    ref = Client.objects.get(tg_id=client.meta['ref_transfer']['ref_id'])

    if father.tg_id == ref.tg_id:
        mess = '❌ Это один и тот же клиент'
        keyboard = keyboards.cancel_button
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    if ref.father == father.tg_id:
        mess = '❌ Реферал уже принадлежит этому рефоводу'
        keyboard = keyboards.cancel_button
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    ref.father = father.tg_id
    ref.save()

    father.ref_count += 1
    father.save()

    client.clear_state()

    mess = '✅ Успешный перенос'
    keyboard = keyboards.functional_menu
    bot.send_message(client, mess, reply_markup=keyboard)


def start_stat_transfer(bot, client):
    client.set_state('get_prev_tg_id')

    keyboard = keyboards.cancel_button
    bot.send_message(client, 'Введите tg id <b>кого перенести</b>', reply_markup=keyboard)

def get_prev_tg_id(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        mess = messages.start_message
        keyboard = keyboards.functional_menu
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    if not message.text.isdigit():
        mess = '❌ Некорректный tg id'
        keyboard = keyboards.cancel_button
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    qs = Client.objects.filter(tg_id=int(message.text))
    if not qs.exists():
        mess = '❌ Такого клиента не существует'
        keyboard = keyboards.cancel_button
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    client.meta['stat_transfer'] = {'prev_tg_id': int(message.text)}
    client.save()
    client.set_state('get_new_tg_id')

    mess = 'Введите tg id <b>куда перенести</b>'
    keyboard = keyboards.cancel_button
    bot.send_message(client, mess, reply_markup=keyboard)

def get_new_tg_id(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        mess = messages.start_message
        keyboard = keyboards.functional_menu
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    if not message.text.isdigit():
        mess = '❌ Некорректный tg id'
        keyboard = keyboards.cancel_button
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    qs = Client.objects.filter(tg_id=int(message.text))
    if not qs.exists():
        mess = '❌ Такого клиента не существует'
        keyboard = keyboards.cancel_button
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    prev_client = Client.objects.get(tg_id=client.meta['stat_transfer']['prev_tg_id'])
    new_client = Client.objects.get(tg_id=int(message.text))

    if prev_client.tg_id == new_client.tg_id:
        mess = '❌ Это один и тот же клиент'
        keyboard = keyboards.cancel_button
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    new_client.count += prev_client.count
    new_client.reject_count += prev_client.reject_count
    new_client.ref_profit += prev_client.ref_profit
    new_client.ref_count += prev_client.ref_count
    new_client.cashback += prev_client.cashback
    new_client.save()

    refferals = Client.objects.filter(father=prev_client.tg_id)
    refferals.update(father=new_client.tg_id)

    prev_client.count = 0
    prev_client.reject_count = 0
    prev_client.ref_profit = 0
    prev_client.ref_count = 0
    prev_client.cashback = 0
    prev_client.save()

    # x = prev_client.tg_id
    # prev_client.tg_id = -1
    # prev_client.save()

    # y = new_client.tg_id
    # new_client.tg_id = x
    # new_client.save()

    # prev_client.tg_id = y
    # prev_client.save()
    # prev_client.tg_id, new_client.tg_id = new_client.tg_id, prev_client.tg_id
    # prev_client.save()
    # new_client.save()

    client.clear_state()

    mess = '✅ Успешный перенос статы'
    keyboard = keyboards.functional_menu
    bot.send_message(client, mess, reply_markup=keyboard)

def start_withdrawal_of_funds(bot, client):
    client.set_state('get_withdrawal_value')
    bot.send_message(client, 'Введи сумму в RUB на вывод средств', reply_markup=keyboards.cancel_button)


def get_withdrawal_value(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return start(bot, client)

    pattern = r'^\d+(\.\d{1,2})?$'

    if re.match(pattern, message.text) is None:
        mess = '❌ Некорректное значение суммы выплаты в рублях'
        keyboard = keyboards.cancel_button
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    client.meta['withdrawal_value'] = round(float(message.text), 2)
    client.save()
    client.set_state('get_withdrawal_purpose')

    mess = 'Напиши цель вывода средств'
    keyboard = keyboards.withdrawal_menu
    bot.send_message(client, mess, reply_markup=keyboard)


def get_withdrawal_purpose(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return start(bot, client)

    client.meta['withdrawal_purpose'] = message.text
    client.save()

    if client.meta['withdrawal_purpose'] == 'Зарплата':
        operators = Operator.objects.all()

        if operators.count() == 0:
            keyboard = keyboards.functional_menu
            bot.send_message(client, '❌ Нет доступных операторов', reply_markup=keyboard)
            return

        keyboard = telebot.types.InlineKeyboardMarkup()
        paginator = Paginator(operators, 3)
        for i in range(1,paginator.num_pages+1):
            buttons = []
            for item in paginator.page(i):
                button = telebot.types.InlineKeyboardButton(text=item.name, callback_data=f'select_withdrawal_oper-{item.id}')
                buttons.append(button)

            keyboard.row(*buttons)

        client.set_state('select_withdrawal_oper')
        bot.send_message(client, 'Выбери оператора', reply_markup=keyboard)

        bot.send_message(client, 'Будь внимателен!', reply_markup=keyboards.cancel_button)
        return

    accept_withdrawal(bot, client)


def select_withdrawal_oper(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return start(bot, client)

    bot.delete_message(client, message.message_id)


def select_withdrawal_oper_callback(bot, client, call):
    data = call.data.split('-')

    operator_id = int(data[1])
    client.meta['withdrawal_op_id'] = operator_id
    client.save()

    accept_withdrawal(bot, client)


def accept_withdrawal(bot, client):
    withdrawal = Withdrawal.objects.create(
        working_shift=WorkingShift.current(),
        purpose=client.meta['withdrawal_purpose'],
        date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        pay_value=client.meta['withdrawal_value']
    )

    withdrawal.save()

    template = bot.get_template(messages.accept_withdrawal_message)
    mess = template.render(withdrawal=withdrawal)
    keyboard = keyboards.start_menu
    bot.send_message(client, mess, reply_markup=keyboard)

    client.clear_state()
    client.update_meta()

    template = bot.get_template(messages.withdrawal_message_info)
    mess = template.render(withdrawal=withdrawal)
    bot.send_report(mess)

    withdrawal_op_id = client.meta.get('withdrawal_op_id', None)

    if withdrawal_op_id is not None and withdrawal.purpose == 'Зарплата':
        operator = Operator.objects.get(id=withdrawal_op_id)
        operator.balance -= withdrawal.pay_value
        operator.save()

        withdrawal.operator = operator
        withdrawal.save()

        if operator.channel_tg_id is not None:
            template = bot.get_template(messages.withdrawal_salary_message_info)
            mess = template.render(withdrawal=withdrawal, balance=operator.balance)

            bot.send_oper_report(operator, mess)

def switch_night(bot, client):
    ws = WorkingShift.current()
    ws.night = not ws.night
    ws.save()

    keyboard = keyboards.functional_menu

    if ws.night:
        bot.send_message(client, '✅ Ночь включена', reply_markup=keyboard)
    else:
        bot.send_message(client, '❌ Ночь выключена', reply_markup=keyboard)

def select_operator(bot, client):
    working_shift = WorkingShift.current()
    if working_shift.operator:
        template = bot.get_template(messages.operator_already_selected_message)
        mess = template.render(operator=working_shift.operator)
        keyboard = keyboards.functional_menu
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    operators = Operator.objects.all()

    if operators.count() == 0:
        keyboard = keyboards.functional_menu
        bot.send_message(client, '❌ Нет доступных операторов', reply_markup=keyboard)
        return

    keyboard = keyboards.cancel_button
    bot.send_message(client, 'Будь внимателен!', reply_markup=keyboard)

    operators = Operator.objects.all()
    keyboard = telebot.types.InlineKeyboardMarkup()
    paginator = Paginator(operators, 3)
    for i in range(1,paginator.num_pages+1):
        buttons = []
        for item in paginator.page(i):
            button = telebot.types.InlineKeyboardButton(text=item.name, callback_data=f'select_oper-{item.id}')
            buttons.append(button)

        keyboard.row(*buttons)

    client.set_state('select_oper')
    mess = messages.select_operator_message
    bot.send_message(client, mess, reply_markup=keyboard)

def select_oper_message(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return start(bot, client)

    bot.delete_message(client, message.message_id)

def select_oper_callback(bot, client, call):
    if client.state != 'select_oper':
        return

    data = call.data.split('-')

    operator = Operator.objects.get(id=int(data[1]))
    working_shift = WorkingShift.current()
    working_shift.operator = operator
    working_shift.save()

    client.clear_state()
    template = bot.get_template(messages.selected_operator_message)
    mess = template.render(operator=operator)
    keyboard = keyboards.functional_menu
    bot.send_message(client, mess, reply_markup=keyboard)

def start_create_duty(bot, client):
    client.set_state('get_duty_amount')
    bot.send_message(client, 'Введи сумму блока в RUB', reply_markup=keyboards.cancel_button)

def get_duty_amount(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return start(bot, client)

    try:
        amount = int(message.text)

        if amount <= 0:
            raise ValueError()

        client.meta['duty_amount'] = amount
        client.save()

        client.set_state('get_duty_client')

        bot.send_message(client, 'Введи никнейм клиента', reply_markup=keyboards.cancel_button)

    except ValueError:
        bot.send_message(client, '❌ Некорректное значение', reply_markup=keyboards.cancel_button)
        return

def get_duty_client(bot, client, message):
    client_name = message.text

    if client_name.startswith('@'):
        client_name = client_name[1:]

    duty = Duty.objects.create(
        working_shift=WorkingShift.current(),
        client_name=client_name,
        amount=client.meta['duty_amount']
    )

    client.clear_state()

    bot.send_message(client, '✅ Записал', reply_markup=keyboards.start_menu)

    template = bot.get_template(messages.duty_info)
    mess = template.render(duty=duty)
    bot.send_report(mess)

def xpay_stats(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    keyboard = keyboards.xpay_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.xpay_balance}</code> RUB', reply_markup=keyboard)

def change_xpay_balance(bot, client):
    client.set_state('get_xpay_balance')
    bot.send_message(client, 'Введите баланс', reply_markup=keyboards.cancel_button)

def get_xpay_balance(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return xpay_stats(bot, client)

    try:
        balance = int(message.text)

    except:
        bot.send_message(client, '❌ Некорректное значение')
        return

    client.clear_state()
    PaymentMethod.objects.select_for_update().filter(id=1).update(xpay_balance=balance)

    xpay_stats(bot, client)


def reset_xpay_balance(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    payment_method.xpay_balance = 0
    payment_method.save()

    keyboard = keyboards.xpay_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.xpay_balance}</code> RUB', reply_markup=keyboard)

def alfateam_stats(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    keyboard = keyboards.alfateam_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.alfateam_balance}</code> RUB', reply_markup=keyboard)

def change_alfateam_balance(bot, client):
    client.set_state('get_alfateam_balance')
    bot.send_message(client, 'Введите баланс', reply_markup=keyboards.cancel_button)

def get_alfateam_balance(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return alfateam_stats(bot, client)

    try:
        balance = int(message.text)

    except:
        bot.send_message(client, '❌ Некорректное значение')
        return

    client.clear_state()
    PaymentMethod.objects.select_for_update().filter(id=1).update(alfateam_balance=balance)
    
    alfateam_stats(bot, client)

def reset_alfateam_balance(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    payment_method.alfateam_balance = 0
    payment_method.save()

    keyboard = keyboards.alfateam_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.alfateam_balance}</code> RUB', reply_markup=keyboard)

def bridgepay_stats(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    keyboard = keyboards.bridgepay_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.bridgepay_balance}</code> RUB', reply_markup=keyboard)

def change_bridgepay_balance(bot, client):
    client.set_state('get_bridgepay_balance')
    bot.send_message(client, 'Введите баланс', reply_markup=keyboards.cancel_button)

def get_bridgepay_balance(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return bridgepay_stats(bot, client)

    try:
        balance = int(message.text)

    except:
        bot.send_message(client, '❌ Некорректное значение')
        return

    client.clear_state()
    PaymentMethod.objects.select_for_update().filter(id=1).update(bridgepay_balance=balance)
    
    bridgepay_stats(bot, client)

def reset_bridgepay_balance(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    payment_method.bridgepay_balance = 0
    payment_method.save()

    keyboard = keyboards.bridgepay_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.bridgepay_balance}</code> RUB', reply_markup=keyboard)


def bridgepay_tj_stats(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    keyboard = keyboards.bridgepay_tj_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.bridgepay_tj_balance}</code> RUB', reply_markup=keyboard)

def change_bridgepay_tj_balance(bot, client):
    client.set_state('get_bridgepay_tj_balance')
    bot.send_message(client, 'Введите баланс', reply_markup=keyboards.cancel_button)

def get_bridgepay_tj_balance(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return bridgepay_tj_stats(bot, client)

    try:
        balance = int(message.text)

    except:
        bot.send_message(client, '❌ Некорректное значение')
        return

    client.clear_state()
    PaymentMethod.objects.select_for_update().filter(id=1).update(bridgepay_tj_balance=balance)
    
    bridgepay_tj_stats(bot, client)

def reset_bridgepay_tj_balance(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    payment_method.bridgepay_tj_balance = 0
    payment_method.save()

    keyboard = keyboards.bridgepay_tj_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.bridgepay_tj_balance}</code> RUB', reply_markup=keyboard)


def secrett_stats(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    keyboard = keyboards.secrett_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.secrett_balance}</code> RUB', reply_markup=keyboard)

def change_secrett_balance(bot, client):
    client.set_state('get_secrett_balance')
    bot.send_message(client, 'Введите баланс', reply_markup=keyboards.cancel_button)

def get_secrett_balance(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return secrett_stats(bot, client)

    try:
        balance = int(message.text)

    except:
        bot.send_message(client, '❌ Некорректное значение')
        return

    client.clear_state()
    PaymentMethod.objects.select_for_update().filter(id=1).update(secrett_balance=balance)
    
    secrett_stats(bot, client)

def reset_secrett_balance(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    payment_method.secrett_balance = 0
    payment_method.save()

    keyboard = keyboards.secrett_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.secrett_balance}</code> RUB', reply_markup=keyboard)


def pspware_stats(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    keyboard = keyboards.pspware_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.pspware_balance}</code> RUB', reply_markup=keyboard)

def change_pspware_balance(bot, client):
    client.set_state('get_pspware_balance')
    bot.send_message(client, 'Введите баланс', reply_markup=keyboards.cancel_button)

def get_pspware_balance(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return pspware_stats(bot, client)

    try:
        balance = int(message.text)

    except:
        bot.send_message(client, '❌ Некорректное значение')
        return

    client.clear_state()
    PaymentMethod.objects.select_for_update().filter(id=1).update(pspware_balance=balance)
    
    pspware_stats(bot, client)

def reset_pspware_balance(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    payment_method.pspware_balance = 0
    payment_method.save()

    keyboard = keyboards.pspware_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.pspware_balance}</code> RUB', reply_markup=keyboard)


def merchant001_stats(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    keyboard = keyboards.merchant001_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.merchant001_balance}</code> RUB', reply_markup=keyboard)

def change_merchant001_balance(bot, client):
    client.set_state('get_merchant001_balance')
    bot.send_message(client, 'Введите баланс', reply_markup=keyboards.cancel_button)

def get_merchant001_balance(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return merchant001_stats(bot, client)

    try:
        balance = int(message.text)

    except:
        bot.send_message(client, '❌ Некорректное значение')
        return

    client.clear_state()
    PaymentMethod.objects.select_for_update().filter(id=1).update(merchant001_balance=balance)
    
    merchant001_stats(bot, client)

def reset_merchant001_balance(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    payment_method.merchant001_balance = 0
    payment_method.save()

    keyboard = keyboards.merchant001_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.merchant001_balance}</code> RUB', reply_markup=keyboard)


def bitzone_stats(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    keyboard = keyboards.bitzone_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.bitzone_balance}</code> RUB', reply_markup=keyboard)

def change_bitzone_balance(bot, client):
    client.set_state('get_bitzone_balance')
    bot.send_message(client, 'Введите баланс', reply_markup=keyboards.cancel_button)

def get_bitzone_balance(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return bitzone_stats(bot, client)
    try:
        balance = int(message.text)
    except:
        bot.send_message(client, '❌ Некорректное значение')
        return
    client.clear_state()
    PaymentMethod.objects.select_for_update().filter(id=1).update(bitzone_balance=balance)

    bitzone_stats(bot, client)

def reset_bitzone_balance(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    payment_method.bitzone_balance = 0
    payment_method.save()
    keyboard = keyboards.bitzone_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.bitzone_balance}</code> RUB', reply_markup=keyboard)   


def wellbit_stats(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    keyboard = keyboards.wellbit_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.wellbit_balance}</code> RUB', reply_markup=keyboard)

def change_wellbit_balance(bot, client):
    client.set_state('get_wellbit_balance')
    bot.send_message(client, 'Введите баланс', reply_markup=keyboards.cancel_button)

def get_wellbit_balance(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return wellbit_stats(bot, client)
    try:
        balance = int(message.text)
    except:
        bot.send_message(client, '❌ Некорректное значение')
        return
    client.clear_state()
    PaymentMethod.objects.select_for_update().filter(id=1).update(wellbit_balance=balance)

    wellbit_stats(bot, client)

def reset_wellbit_balance(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    payment_method.wellbit_balance = 0
    payment_method.save()
    keyboard = keyboards.wellbit_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.wellbit_balance}</code> RUB', reply_markup=keyboard)  


def extasypay_stats(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    keyboard = keyboards.extasypay_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.extasypay_balance}</code> RUB', reply_markup=keyboard)

def change_extasypay_balance(bot, client):
    client.set_state('get_extasypay_balance')
    bot.send_message(client, 'Введите баланс', reply_markup=keyboards.cancel_button)

def get_extasypay_balance(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return extasypay_stats(bot, client)
    try:
        balance = int(message.text)
    except:
        bot.send_message(client, '❌ Некорректное значение')
        return
    client.clear_state()
    PaymentMethod.objects.select_for_update().filter(id=1).update(extasypay_balance=balance)

    extasypay_stats(bot, client)

def reset_extasypay_balance(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    payment_method.extasypay_balance = 0
    payment_method.save()
    keyboard = keyboards.extasypay_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.extasypay_balance}</code> RUB', reply_markup=keyboard)  


def infinitypay_stats(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    keyboard = keyboards.infinitypay_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.infinitypay_balance}</code> RUB', reply_markup=keyboard)

def change_infinitypay_balance(bot, client):
    client.set_state('get_infinitypay_balance')
    bot.send_message(client, 'Введите баланс', reply_markup=keyboards.cancel_button)

def get_infinitypay_balance(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return infinitypay_stats(bot, client)
    try:
        balance = int(message.text)
    except:
        bot.send_message(client, '❌ Некорректное значение')
        return
    client.clear_state()
    PaymentMethod.objects.select_for_update().filter(id=1).update(infinitypay_balance=balance)

    infinitypay_stats(bot, client)

def reset_infinitypay_balance(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    payment_method.infinitypay_balance = 0
    payment_method.save()
    keyboard = keyboards.infinitypay_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.infinitypay_balance}</code> RUB', reply_markup=keyboard)   


def get_provider_balances(bot, client):
    payment_method = PaymentMethod.objects.first()
    template = bot.get_template(messages.provider_balances_message)
    mess = template.render(payment_method=payment_method)
    bot.send_message(client, mess, reply_markup=keyboards.start_menu)

def vita_stats(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    keyboard = keyboards.vita_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.vita_balance}</code> RUB', reply_markup=keyboard)

def change_vita_balance(bot, client):
    client.set_state('get_vita_balance')
    bot.send_message(client, 'Введите баланс', reply_markup=keyboards.cancel_button)

def get_vita_balance(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return vita_stats(bot, client)
    try:
        balance = int(message.text)
    except:
        bot.send_message(client, '❌ Некорректное значение')
        return
    client.clear_state()
    PaymentMethod.objects.select_for_update().filter(id=1).update(vita_balance=balance)

    vita_stats(bot, client)

def reset_vita_balance(bot, client):
    payment_method = PaymentMethod.objects.get(id=1)
    payment_method.vita_balance = 0
    payment_method.save()
    keyboard = keyboards.vita_menu
    bot.send_message(client, f'Баланс: <code>{payment_method.vita_balance}</code> RUB', reply_markup=keyboard)   


def get_provider_balances(bot, client):
    payment_method = PaymentMethod.objects.first()
    template = bot.get_template(messages.provider_balances_message)
    mess = template.render(payment_method=payment_method)
    bot.send_message(client, mess, reply_markup=keyboards.start_menu)




