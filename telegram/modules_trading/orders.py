from . import messages, keyboards
from .start import start

from trading.models import Order


def reject_order(bot, client, call):
    data = call.data.split('-')
    trader = client.trader
    order = Order.objects.filter(id=int(data[1]), trader=trader, status='pending').first()

    if order is not None:
        order.reject()
        order.refresh_from_db()

        template = bot.get_template(messages.order_message)
        mess = template.render(order=order)

        bot.edit_message_text(client, call.message.message_id, mess, reply_markup=None)


def confirm_order(bot, client, call):
    data = call.data.split('-')
    trader = client.trader
    order = Order.objects.filter(id=int(data[1]), trader=trader, status='pending').first()

    if order is not None:
        order.confirm()
        order.refresh_from_db()

        template = bot.get_template(messages.order_message)
        mess = template.render(order=order)

        bot.edit_message_text(client, call.message.message_id, mess, reply_markup=None)


def change_order_amount(bot, client, call):
    data = call.data.split('-')
    trader = client.trader
    order = Order.objects.filter(id=int(data[1]), trader=trader, status='pending').first()

    if order is not None:
        client.meta['change_order_amount'] = {'id': order.id, 'message_id': call.message.message_id}
        client.save()

        mess = messages.get_new_order_amount_message
        keyboard = keyboards.cancel_button
        client.set_state('get_new_order_amount')

        bot.send_message(client, mess, reply_markup=keyboard)


def get_new_order_amount(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return start(bot, client)

    try:
        amount = int(message.text)

    except ValueError:
        mess = messages.incorrect_amount_message
        keyboard = keyboards.cancel_button

        return bot.send_message(client, mess, reply_markup=keyboard)

    trader = client.trader
    order = Order.objects.filter(
        id=client.meta['change_order_amount']['id'],
        trader=trader,
        status='pending'
    ).first()

    if order is not None:
        order.change_amount(amount)
        order.refresh_from_db()

        template = bot.get_template(messages.order_message)
        mess = template.render(order=order)
        keyboard = keyboards.get_order_keyboard(order)
        client.clear_state()

        bot.edit_message_text(
            client,
            client.meta['change_order_amount']['message_id'],
            mess,
            reply_markup=keyboard
        )

        start(bot, client)


def get_orders_list(bot, client):
    trader = client.trader
    orders = Order.objects.filter(trader=trader).order_by('-id')[:10]

    if orders.count() == 0:
        mess = 'История сделок пуста'
        keyboard = keyboards.start_menu

        return bot.send_message(client, mess, reply_markup=keyboard)

    template = bot.get_template(messages.orders_message)
    mess = template.render(orders=orders)
    keyboard = keyboards.start_menu

    bot.send_message(client, mess, reply_markup=keyboard)







