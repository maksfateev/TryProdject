from . import start, settings, requisites, orders, working_shift


message_handlers = {
    '/start': start.start,
    '⬅️ Назад': start.start,
    'unknown_command': start.unknown_command,
    '⚙️ Настройки': settings.start,
    '💳 Реквизиты': requisites.start,
    '➕ Добавить': requisites.add_requisites,
    '📋 Мои реквизиты': requisites.get_requisites_list,
    '🧾 Сделки': orders.get_orders_list,
    '📠 Закрыть смену': working_shift.close_working_shift,
}

state_handlers = {
    'get_requisites_bank': requisites.get_requisites_bank,
    'get_requisites_cardholder': requisites.get_requisites_cardholder,
    'get_requisites_card_number': requisites.get_requisites_card_number,
    'get_requisites_sbp_number': requisites.get_requisites_sbp_number,
    'get_new_order_amount': orders.get_new_order_amount,
    'accept_close_working_shift': working_shift.accept_close_working_shift,
}

callback_handlers = {
    'switch': settings.switch,
    'switch_requisites_list': requisites.switch_requisites_list,
    'requisite_details': requisites.requisite_details,
    'switch_card_number': requisites.switch_card_number,
    'switch_sbp_number': requisites.switch_sbp_number,
    'delete_requisite': requisites.delete_requisite,
    'confirm_delete_requisite': requisites.confirm_delete_requisite,
    'reject_order': orders.reject_order,
    'confirm_order': orders.confirm_order,
    'change_order_amount': orders.change_order_amount,
}
