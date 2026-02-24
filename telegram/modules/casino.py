from . import messages, keyboards


def start(bot, client):
    bot.send_message(client, '🎰 Погрузитесь в мир азарта с нашим казино-ботом:\n@casino_men9La_bot', reply_markup=keyboards.start_menu)