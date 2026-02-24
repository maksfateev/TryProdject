from . import messages, keyboards
from .start import start

from trading.models import WorkingShift, Order


def close_working_shift(bot, client):
    mess = messages.accept_close_working_shift_message
    keyboard = keyboards.accept_close_working_shift_menu
    client.set_state('accept_close_working_shift')

    bot.send_message(client, mess, reply_markup=keyboard)


def accept_close_working_shift(bot, client, message):
    if message.text == '❌ Нет':
        client.clear_state()
        return start(bot, client)

    elif message.text == '✅ Да':
        trader = client.trader
        orders = Order.objects.filter(
            trader=trader,
            working_shift__isnull=True,
            status__in=['confirmed', 'rejected']
        )

        if orders.count() == 0:
            mess = '⛔️ У вас нет завершенных заявок'
            keyboard = keyboards.start_menu
            client.clear_state()

            return bot.send_message(client, mess, reply_markup=keyboard)

        working_shift = WorkingShift.objects.create(trader=trader)
        orders.update(working_shift=working_shift)

        template = bot.get_template(messages.working_shift_message)
        mess = template.render(working_shift=working_shift)
        keyboard = keyboards.start_menu
        client.clear_state()

        bot.send_message(client, mess, reply_markup=keyboard)

    else:
        bot.delete_message(client, message.message_id)

