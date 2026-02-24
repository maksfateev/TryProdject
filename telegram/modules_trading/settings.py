from . import messages, keyboards


def start(bot, client):
    mess = messages.start_message
    keyboard = keyboards.get_settings_menu(client.trader)

    bot.send_message(client, mess, reply_markup=keyboard)


def switch(bot, client, call):
    data = call.data.split('-')
    trader = client.trader

    match data[1]:
        case 'in_work':
            trader.in_work = not trader.in_work

        case _:
            return

    trader.save()
    keyboard = keyboards.get_settings_menu(trader)

    bot.edit_message_reply_markup(client, call.message.message_id, reply_markup=keyboard)
