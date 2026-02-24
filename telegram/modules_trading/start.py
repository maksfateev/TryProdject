from . import messages, keyboards


def start(bot, client):
    client.clear_state()
    client.update_meta()

    mess = messages.start_message
    keyboard = keyboards.start_menu

    bot.send_message(client, mess, reply_markup=keyboard)


def unknown_command(bot, client, message):
    bot.delete_message(client, message.message_id)
