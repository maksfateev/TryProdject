import telebot

from django.core.paginator import Paginator


start_menu = telebot.types.ReplyKeyboardMarkup(True)
start_menu.row('💳 Реквизиты', '🧾 Сделки')
start_menu.row('⚙️ Настройки', '📠 Закрыть смену')


cancel_button = telebot.types.ReplyKeyboardMarkup(True).row('❌ Отмена')


def get_settings_menu(trader):
    keyboard = telebot.types.InlineKeyboardMarkup()

    in_work_flag = '🟢' if trader.in_work else '🔴'
    in_work_button = telebot.types.InlineKeyboardButton(
        text=f'{in_work_flag} В работе',
        callback_data='switch-in_work'
    )
    keyboard.row(in_work_button)

    return keyboard


requisites_menu = telebot.types.ReplyKeyboardMarkup(True)
requisites_menu.row('➕ Добавить', '📋 Мои реквизиты')
requisites_menu.row('⬅️ Назад')


def get_requisites_list_menu(cards, page=1):
    keyboard = telebot.types.InlineKeyboardMarkup()
    paginator = Paginator(cards.order_by('-id'), 10)

    if page > paginator.num_pages:
        page = paginator.num_pages

    for card in paginator.page(page):
        status_flag = '🔴' if card.status == 'ready' else '🟢'
        label = f'{status_flag} {card.cardholder_name}/{card.bank}/{card.short_number}'
        card_button = telebot.types.InlineKeyboardButton(
            text=label,
            callback_data=f'requisite_details-{card.id}'
        )
        keyboard.row(card_button)

    switch_buttons = []

    if paginator.page(page).has_previous():
        prev_button = telebot.types.InlineKeyboardButton(
            text='⬅️',
            callback_data=f'switch_requisites_list-{page-1}'
        )
        switch_buttons.append(prev_button)

    if paginator.page(page).has_next():
        next_button = telebot.types.InlineKeyboardButton(
            text='➡️',
            callback_data=f'switch_requisites_list-{page+1}'
        )
        switch_buttons.append(next_button)

    keyboard.row(*switch_buttons)
    return keyboard


def get_requisite_details_menu(card, return_to_page=1):
    keyboard = telebot.types.InlineKeyboardMarkup()

    if card.status in ['worked_all', 'worked_card']:
        card_flag = '🟢'

    else:
        card_flag = '🔴'

    card_button = telebot.types.InlineKeyboardButton(
        text=f'{card_flag} Номер карты',
        callback_data=f'switch_card_number-{card.id}'
    )

    if card.status in ['worked_all', 'worked_sbp']:
        sbp_flag = '🟢'

    else:
        sbp_flag = '🔴'

    sbp_button = telebot.types.InlineKeyboardButton(
        text=f'{sbp_flag} СБП',
        callback_data=f'switch_sbp_number-{card.id}'
    )

    keyboard.row(card_button, sbp_button)

    delete_button = telebot.types.InlineKeyboardButton(
        text='❗️ Удалить',
        callback_data=f'delete_requisite-{card.id}'
    )
    keyboard.row(delete_button)

    return_button = telebot.types.InlineKeyboardButton(
        text='⬅️ Назад',
        callback_data=f'switch_requisites_list-{return_to_page}'
    )
    keyboard.row(return_button)

    return keyboard


def get_delete_requisite_menu(card):
    keyboard = telebot.types.InlineKeyboardMarkup()

    confirm_button = telebot.types.InlineKeyboardButton(
        text='Да',
        callback_data=f'confirm_delete_requisite-{card.id}'
    )
    cancel_button = telebot.types.InlineKeyboardButton(
        text='Нет',
        callback_data=f'requisite_details-{card.id}'
    )
    keyboard.row(confirm_button, cancel_button)

    return keyboard


def get_order_keyboard(order):
    if order.status == 'pending':
        keyboard = telebot.types.InlineKeyboardMarkup()

        confirm_button = telebot.types.InlineKeyboardButton(
            text='✅ Подтвердить',
            callback_data=f'confirm_order-{order.id}'
        )
        reject_button = telebot.types.InlineKeyboardButton(
            text='❌ Отклонить',
            callback_data=f'reject_order-{order.id}'
        )
        keyboard.row(confirm_button, reject_button)

        change_amount_button = telebot.types.InlineKeyboardButton(
            text='✏️ Изменить сумму',
            callback_data=f'change_order_amount-{order.id}'
        )
        keyboard.row(change_amount_button)

        return keyboard


accept_close_working_shift_menu = telebot.types.ReplyKeyboardMarkup(True)
accept_close_working_shift_menu.row('✅ Да', '❌ Нет')






