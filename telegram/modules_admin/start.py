from . import messages, keyboards
from telegram.models import Bill, WorkingShift
from wallets import XMRWallet

def start(bot, client, message=None):
	client.clear_state()
	mess = messages.start_message
	keyboard = keyboards.start_menu
	bot.send_message(client, mess, reply_markup=keyboard)

def unknown_command(bot, client, message):
	data = message.text.split()
	keyboard = keyboards.start_menu

	match data[0].lower():
		case 'чек':
			if len(data) != 4:
				mess = messages.incorrect_bill_message
				bot.send_message(client, mess, reply_markup=keyboard)
				return

			try:
				rub_value = int(data[1])
				pay_value = int(data[3])
			except:
				mess = messages.incorrect_bill_message
				keyboard = keyboards.start_menu
				bot.send_message(client, mess, reply_markup=keyboard)
				return

			bill = Bill.objects.create(
				working_shift=WorkingShift.current(),
				bill_type='Отправка',
				rub_value=rub_value,
				pay_value=pay_value
			)

			template = bot.get_template(messages.send_bill_message)
			mess = template.render(bill=bill)
			bot.send_message(client, mess, reply_markup=keyboard)
			bot.send_report(mess)

		case 'закуп':
			if len(data) != 5:
				mess = messages.incorrect_bill_message
				bot.send_message(client, mess, reply_markup=keyboard)
				return

			try:
				rub_value = int(data[2])
				pay_value = int(data[4])
			except:
				mess = messages.incorrect_bill_message
				keyboard = keyboards.start_menu
				bot.send_message(client, mess, reply_markup=keyboard)
				return

			bill = Bill.objects.create(
				working_shift=WorkingShift.current(),
				bill_type='Закупка',
				rub_value=rub_value,
				pay_value=pay_value
			)

			template = bot.get_template(messages.purchase_bill_message)
			mess = template.render(bill=bill)
			bot.send_message(client, mess, reply_markup=keyboard)
			bot.send_report(mess)

		case _:
			return start(bot, client)




















