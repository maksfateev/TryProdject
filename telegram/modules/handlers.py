from . import start, office, contacts, sell_crypt, buy_crypt, casino, reviews, wallets

message_handlers = {
	'/start': start.start,
	'unknown_command': start.unknown_command,
	'💻 Личный кабинет': office.start,
	'⬅️ Назад': start.start,
	'🏷 Промокод': office.start_promocode,
	'🧑‍💻 Контакты': contacts.start,
	'📉 Продать': sell_crypt.sell_crypt,
	'📈 Купить': buy_crypt.buy_crypt,
	'🔄 Купить BTC': buy_crypt.buy_btc,
	'🔄 Купить LTC': buy_crypt.buy_ltc,
	'🔄 Купить XMR': buy_crypt.buy_xmr,
	'🔄 Купить USDT-TRC20': buy_crypt.buy_usdt,
	'Продать BTC': sell_crypt.sell_btc,
	'Продать LTC': sell_crypt.sell_ltc,
	'Продать XMR': sell_crypt.sell_xmr,
	'Продать USDT': sell_crypt.sell_usdt,
	'Вывести реф. счет': office.create_withdrawal,
    '📥 Пополнить через обменник': wallets.deposit_from_exchange,
    '⬇️ Пополнить': wallets.deposit_action,
	'🎰 Испытай удачу': office.get_luck,
	'🧮 Калькулятор': office.start_calculate,
	'🎰 Казино': casino.start,
    '🔐 Кошелек': wallets.start,
	'💰 Баланс': wallets.balance,
	'⬇️ Депозит': wallets.deposit,
	'📜 История': wallets.history,
	'⬆️ Вывод': wallets.withdrawal,
}

state_handlers = {
	'get_value': buy_crypt.get_value,
	'choice_payment_method': buy_crypt.choice_payment_method,
	'get_address': buy_crypt.get_address,
	'choice_action': buy_crypt.choice_action,
    'get_paycheck': buy_crypt.get_paycheck,
    'activate_cashback': buy_crypt.activate_cashback_message,
    'accept_monobank': buy_crypt.accept_monobank,

	'choice_calc_crypt': office.choice_calc_crypt,
    'get_promocode': office.get_promocode,
	'get_calc_value': office.get_calc_value,
	'accept_withdrawal': office.accept_withdrawal,

	'get_card_requisites': sell_crypt.get_card_requisites,
	'get_sell_value': sell_crypt.get_value,
	'choice_sell_payment_method': sell_crypt.choice_payment_method,
	'get_sbp_requisites': sell_crypt.get_sbp_requisites,
	'accept_sell': sell_crypt.accept_sell,
	'get_bank_name': sell_crypt.get_bank_name,

    'get_review_text': reviews.get_review_text,

    'choice_deposit_crypt': wallets.choice_deposit_crypt,
    'choice_history_crypt': wallets.choice_history_crypt,
    'choice_history_category': wallets.choice_history_category,
    'choice_withdrawal_crypt': wallets.choice_withdrawal_crypt,
    'get_withdrawal_address': wallets.get_withdrawal_address,
    'get_withdrawal_amount': wallets.get_withdrawal_amount,
    'confirm_withdrawal': wallets.confirm_withdrawal,
}

callback_handlers = {
	'choice_promo': buy_crypt.choice_promo,
	'payment_method': buy_crypt.get_payment_method,
	'cancel_order': buy_crypt.cancel_order,
	'accept_pay': buy_crypt.accept_pay,
    'send_paycheck': buy_crypt.start_paychek,
    'cancel_paycheck': buy_crypt.cancel_paychek,
	'activate_cashback': buy_crypt.activate_cashback,
	'deactivate_cashback': buy_crypt.deactivate_cashback,
	'start_get_address': buy_crypt.start_get_address,

    'new_deposit_address': wallets.new_deposit_address,

	'payment_method_sell': sell_crypt.get_payment_method,
    
    'get_review': reviews.get_review,
    
}