from . import messages, keyboards

from general_settings.models import Card


def start(bot, client):
    mess = messages.start_message
    keyboard = keyboards.requisites_menu

    bot.send_message(client, mess, reply_markup=keyboard)


def add_requisites(bot, client):
    mess = messages.get_requisites_bank_message
    keyboard = keyboards.cancel_button
    client.set_state('get_requisites_bank')

    bot.send_message(client, mess, reply_markup=keyboard)


def get_requisites_bank(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return start(bot, client)

    client.meta['add_requisites'] = {'bank': message.text}
    client.save()


    mess = messages.get_requisites_cardholder_message
    keyboard = keyboards.cancel_button
    client.set_state('get_requisites_cardholder')

    bot.send_message(client, mess, reply_markup=keyboard)


def get_requisites_cardholder(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return start(bot, client)

    client.meta['add_requisites']['cardholder'] = message.text
    client.save()

    mess = messages.get_requisites_card_number_message
    keyboard = keyboards.cancel_button
    client.set_state('get_requisites_card_number')

    bot.send_message(client, mess, reply_markup=keyboard)


def get_requisites_card_number(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return start(bot, client)

    client.meta['add_requisites']['card_number'] = message.text
    client.save()

    mess = messages.get_requisites_sbp_number_message
    keyboard = keyboards.cancel_button
    client.set_state('get_requisites_sbp_number')

    bot.send_message(client, mess, reply_markup=keyboard)


def get_requisites_sbp_number(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return start(bot, client)

    client.meta['add_requisites']['sbp_number'] = message.text
    client.save()

    card = Card.objects.create(
        trader=client.trader,
        bank=client.meta['add_requisites']['bank'],
        cardholder_name=client.meta['add_requisites']['cardholder'],
        card_number=client.meta['add_requisites']['card_number'],
        phone_number=client.meta['add_requisites']['sbp_number']
    )

    template = bot.get_template(messages.card_message)
    mess = template.render(card=card)
    keyboard = keyboards.requisites_menu
    client.clear_state()

    bot.send_message(client, mess, reply_markup=keyboard)


def get_requisites_list(bot, client):
    trader = client.trader
    cards = Card.objects.filter(trader=trader, status__in=['worked_all', 'worked_card', 'worked_sbp', 'ready'])

    mess = messages.start_message
    keyboard = keyboards.get_requisites_list_menu(cards)

    bot.send_message(client, mess, reply_markup=keyboard)


def switch_requisites_list(bot, client, call):
    data = call.data.split('-')
    trader = client.trader
    cards = Card.objects.filter(trader=trader, status__in=['worked_all', 'worked_card', 'worked_sbp', 'ready'])

    mess = messages.start_message
    keyboard = keyboards.get_requisites_list_menu(cards, page=int(data[1]))

    client.meta['requisites_list_page'] = int(data[1])
    client.save()

    bot.edit_message_text(client, call.message.message_id, mess, reply_markup=keyboard)


def requisite_details(bot, client, call):
    data = call.data.split('-')
    trader = client.trader
    card = Card.objects.filter(
        id=int(data[1]),
        trader=trader,
        status__in=['worked_all', 'worked_card', 'worked_sbp', 'ready']
    ).first()

    if card is not None:
        template = bot.get_template(messages.card_message)
        mess = template.render(card=card)
        keyboard = keyboards.get_requisite_details_menu(
            card,
            return_to_page=client.meta.get('requisites_list_page', 1)
        )

        bot.edit_message_text(client, call.message.message_id, mess, reply_markup=keyboard)


def switch_card_number(bot, client, call):
    data = call.data.split('-')
    trader = client.trader
    card = Card.objects.filter(
        id=int(data[1]),
        trader=trader,
        status__in=['worked_all', 'worked_card', 'worked_sbp', 'ready']
    ).first()

    if card is not None:
        match card.status:
            case 'ready':
                card.status = 'worked_card'

            case 'worked_sbp':
                card.status = 'worked_all'

            case 'worked_card':
                card.status = 'ready'

            case 'worked_all':
                card.status = 'worked_sbp'

        card.save()

        template = bot.get_template(messages.card_message)
        mess = template.render(card=card)
        keyboard = keyboards.get_requisite_details_menu(
            card,
            return_to_page=client.meta.get('requisites_list_page', 1)
        )

        bot.edit_message_text(client, call.message.message_id, mess, reply_markup=keyboard)


def switch_sbp_number(bot, client, call):
    data = call.data.split('-')
    trader = client.trader
    card = Card.objects.filter(
        id=int(data[1]),
        trader=trader,
        status__in=['worked_all', 'worked_card', 'worked_sbp', 'ready']
    ).first()

    if card is not None:
        match card.status:
            case 'ready':
                card.status = 'worked_sbp'

            case 'worked_sbp':
                card.status = 'ready'

            case 'worked_card':
                card.status = 'worked_all'

            case 'worked_all':
                card.status = 'worked_card'

        card.save()

        template = bot.get_template(messages.card_message)
        mess = template.render(card=card)
        keyboard = keyboards.get_requisite_details_menu(
            card,
            return_to_page=client.meta.get('requisites_list_page', 1)
        )

        bot.edit_message_text(client, call.message.message_id, mess, reply_markup=keyboard)


def delete_requisite(bot, client, call):
    data = call.data.split('-')
    trader = client.trader
    card = Card.objects.filter(
        id=int(data[1]),
        trader=trader,
        status__in=['worked_all', 'worked_card', 'worked_sbp', 'ready']
    ).first()

    if card is not None:
        mess = messages.delete_requisite_message
        keyboard = keyboards.get_delete_requisite_menu(card)

        bot.edit_message_text(client, call.message.message_id, mess, reply_markup=keyboard)


def confirm_delete_requisite(bot, client, call):
    data = call.data.split('-')
    trader = client.trader
    card = Card.objects.filter(
        id=int(data[1]),
        trader=trader,
        status__in=['worked_all', 'worked_card', 'worked_sbp', 'ready']
    ).first()

    if card is not None:
        card.status = 'deleted'
        card.save()

        cards = Card.objects.filter(trader=trader, status__in=['worked_all', 'worked_card', 'worked_sbp', 'ready'])

        mess = messages.start_message
        keyboard = keyboards.get_requisites_list_menu(cards, page=client.meta.get('requisites_list_page', 1))

        bot.edit_message_text(client, call.message.message_id, mess, reply_markup=keyboard)
