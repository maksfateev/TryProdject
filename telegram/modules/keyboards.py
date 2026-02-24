import telebot

start_menu = telebot.types.ReplyKeyboardMarkup(True)
start_menu.row('📈 Купить', '📉 Продать')
start_menu.row('🔐 Кошелек')
start_menu.row('💻 Личный кабинет', '🧑‍💻 Контакты')

buy_crypt_menu = telebot.types.ReplyKeyboardMarkup(True)
buy_crypt_menu.row('🔄 Купить BTC', '🔄 Купить LTC')
buy_crypt_menu.row('🔄 Купить XMR', '🔄 Купить USDT-TRC20')
buy_crypt_menu.row('⬅️ Назад')

accept_monobank_keyboard = telebot.types.ReplyKeyboardMarkup(True)
accept_monobank_keyboard.row('Я понимаю', '❌ Отмена')

sell_crypt_menu = telebot.types.ReplyKeyboardMarkup(True)
sell_crypt_menu.row('Продать BTC', 'Продать LTC')
# sell_crypt_menu.row('Продать XMR', 'Продать USDT')
sell_crypt_menu.row('⬅️ Назад')

order_sell_menu = telebot.types.ReplyKeyboardMarkup(True)
order_sell_menu.row('✅ Продолжить', '❌ Отмена')

office_menu = telebot.types.ReplyKeyboardMarkup(True)
office_menu.row('🏷 Промокод', 'Вывести реф. счет')
office_menu.row('🎰 Испытай удачу')
office_menu.row('🧮 Калькулятор')
office_menu.row('⬅️ Назад')

cancel_button = telebot.types.ReplyKeyboardMarkup(True).row('❌ Отмена')

order_menu = telebot.types.InlineKeyboardMarkup()
order_menu.row(
	telebot.types.InlineKeyboardButton(text='✅ Я оплатил', callback_data=f"accept_pay")
)
order_menu.row(
	telebot.types.InlineKeyboardButton(text='❌ Отменить заявку', callback_data=f"cancel_order")
)

choice_calc_crypt_menu = telebot.types.ReplyKeyboardMarkup(True)
choice_calc_crypt_menu.row('BTC', 'LTC', 'XMR', 'USDT')
choice_calc_crypt_menu.row('❌ Отмена')

accept_withdrawal_keyboard = telebot.types.ReplyKeyboardMarkup(True)
accept_withdrawal_keyboard.row('✅ Да', '❌ Нет')


wallets_menu = telebot.types.ReplyKeyboardMarkup(True)
wallets_menu.row('⬆️ Вывод', '⬇️ Пополнить')
wallets_menu.row('💰 Баланс', '📜 История')
wallets_menu.row('⬅️ Назад')

deposit_action_menu = telebot.types.ReplyKeyboardMarkup(True)
deposit_action_menu.row('⬇️ Депозит', '📥 Пополнить через обменник')
deposit_action_menu.row('⬅️ Назад')


def get_paychek_menu(order_id):
    paycheck_menu = telebot.types.InlineKeyboardMarkup()
    paycheck_menu.row(
        telebot.types.InlineKeyboardButton(text='👍 Прислать чек', callback_data=f"send_paycheck-{order_id}")
    )
    paycheck_menu.row(
        telebot.types.InlineKeyboardButton(text='👎 Без чека', callback_data=f"cancel_paycheck-{order_id}")
    )

    return paycheck_menu


deposit_menu = telebot.types.ReplyKeyboardMarkup(True)
deposit_menu.row('BTC', 'LTC', 'XMR', 'USDT')
deposit_menu.row('❌ Отмена')


def get_new_deposit_address_keyboard(crypt):
    new_deposit_address = telebot.types.InlineKeyboardMarkup()
    new_deposit_address.row(
        telebot.types.InlineKeyboardButton(text='Сгенерировать новый адрес', callback_data=f"new_deposit_address-{crypt}")
    )

    return new_deposit_address

history_crypt_menu = telebot.types.ReplyKeyboardMarkup(True)
history_crypt_menu.row('BTC', 'LTC', 'XMR', 'USDT')
history_crypt_menu.row('❌ Отмена')

history_category_menu = telebot.types.ReplyKeyboardMarkup(True)
history_category_menu.row('Вывод', 'Депозит')
history_category_menu.row('❌ Отмена')

withdrawal_crypt_menu = telebot.types.ReplyKeyboardMarkup(True)
withdrawal_crypt_menu.row('BTC', 'LTC', 'XMR', 'USDT')
withdrawal_crypt_menu.row('❌ Отмена')

confirm_withdrawal_menu = telebot.types.ReplyKeyboardMarkup(True)
confirm_withdrawal_menu.row('✅ Подтвердить', '❌ Отмена')