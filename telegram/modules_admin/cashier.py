from . import messages, keyboards
from telegram.models import WorkingShift, Bill


def start(bot, client):
	client.set_state('cashier_accept_close')
	mess = messages.chashier_start_message
	keyboard = keyboards.cashier_menu
	bot.send_message(client, mess, reply_markup=keyboard)

def cashier_accept_close(bot, client, message):
	if message.text == '❌ Нет':
		client.clear_state()
		mess = messages.start_message
		keyboard = keyboards.functional_menu
		bot.send_message(client, mess, reply_markup=keyboard)

	elif message.text == '✅ Да':
		working_shift = WorkingShift.current()
		if not working_shift.check_for_close():
			client.clear_state()
			mess = messages.cant_close_cashier_message
			keyboard = keyboards.start_menu
			bot.send_message(client, mess, reply_markup=keyboard)
			return
		working_shift.close()
		working_shift.report(bot)

		client.clear_state()
		template = bot.get_template(messages.working_shift_info_message)
		mess = template.render(working_shift=working_shift)
		keyboard = keyboards.start_menu
		bot.send_message(client, mess, reply_markup=keyboard)

	else:
		bot.delete_message(client, message.message_id)
		
def start_trading_purchase(bot, client):
    mess = messages.get_trader_name
    keyboard = keyboards.cancel_button
    client.set_state('get_trader_name')

    bot.send_message(client, mess, reply_markup=keyboard)


def get_trader_name(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()

        mess = messages.start_message
        keyboard = keyboards.functional_menu
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    client.meta['trading_purchase'] = {'trader': message.text}
    client.save()

    mess = messages.get_trading_purchase_amount_message
    keyboard = keyboards.cancel_button
    client.set_state('get_trading_purchase_amount')

    bot.send_message(client, mess, reply_markup=keyboard)


def get_trading_purchase_amount(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()

        mess = messages.start_message
        keyboard = keyboards.functional_menu
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    try:
        amount = int(message.text)

    except ValueError:
        mess = messages.incorrect_pay_value_message
        keyboard = keyboards.cancel_button

        bot.send_message(client, mess, reply_markup=keyboard)
        return

    client.meta['trading_purchase']['amount'] = amount
    client.save()

    mess = messages.get_trading_purchase_percent_message
    keyboard = keyboards.cancel_button
    client.set_state('get_trading_purchase_percent')

    bot.send_message(client, mess, reply_markup=keyboard)


def get_trading_purchase_percent(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()

        mess = messages.start_message
        keyboard = keyboards.functional_menu
        bot.send_message(client, mess, reply_markup=keyboard)
        return

    try:
        percent = float(message.text.replace(',', '.'))

    except ValueError:
        mess = messages.incorrect_pay_value_message
        keyboard = keyboards.cancel_button

        bot.send_message(client, mess, reply_markup=keyboard)
        return

    amount = client.meta['trading_purchase']['amount']

    pay_value = amount
    rub_value = pay_value - (amount / 100 * percent)
    bill = Bill.objects.create(
        working_shift=WorkingShift.current(),
        bill_type='Закупка',
        rub_value=rub_value,
        pay_value=pay_value
    )

    template = bot.get_template(messages.trading_purchase_message)
    mess = template.render(bill=bill, percent=percent, trader=client.meta['trading_purchase']['trader'])
    keyboard = keyboards.functional_menu
    client.clear_state()

    bot.send_message(client, mess, reply_markup=keyboard)
    bot.send_report(mess)
