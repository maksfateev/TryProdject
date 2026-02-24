from . import messages, keyboards

from general_settings.models import PaymentMethod


def start(bot, client):
    client.set_state('get_reqs_type')

    bot.send_message(client, 'Выберите метод оплаты', reply_markup=keyboards.get_reqs_menu)


def get_reqs_type(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()

        bot.send_message(client, messages.start_message, reply_markup=keyboards.start_menu)
        return

    if message.text == 'Номер карты':
        client.meta['get_reqs'] = {'reqs_type': 'card'}

    elif message.text == 'СБП':
        client.meta['get_reqs'] = {'reqs_type': 'sbp'}

    else:
        return

    client.save()
    client.set_state('get_reqs_amount')

    bot.send_message(client, 'Введите сумму оплаты', reply_markup=keyboards.cancel_button)


def get_reqs_amount(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()

        bot.send_message(client, messages.start_message, reply_markup=keyboards.start_menu)
        return

    try:
        amount = int(message.text)

    except ValueError:
        bot.send_message(client, '❌ Некорректное значение', reply_markup=keyboards.cancel_button)
        return

    client.clear_state()

    try:
        payment_method = PaymentMethod.objects.first()
        reqs = payment_method.get_requisites(amount, client.meta['get_reqs']['reqs_type'])

        mess = f'ID {reqs["provider"]}: <code>{reqs["label"]}</code>\nРеквизиты: <code>{reqs["reqs"]}</code> {reqs["bank"]}'
        bot.send_message(client, mess, reply_markup=keyboards.start_menu)

    except Exception as e:
        bot.send_message(client, str(e), reply_markup=keyboards.start_menu)
