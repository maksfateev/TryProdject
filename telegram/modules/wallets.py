import re
import uuid
from decimal import Decimal

from django.db import transaction as db_transaction

from . import messages, keyboards

from telegram.models import Wallet, WalletTransaction, Order
from general_settings.models import CryptSettings, WalletsSettings

from wallets import BTCWallet, LTCWallet, XMRWallet, USDTWallet, display_decimal

wallets = {
    'BTC': BTCWallet.Wallet,
    'LTC': LTCWallet.Wallet,
    'XMR': XMRWallet.Wallet,
    'USDT': USDTWallet.Wallet
}

def start(bot, client):
    commissions = {}
    for key, _ in wallets.items():
        wallets_settings = WalletsSettings.objects.first()
        withdrawal_commission = Decimal(wallets[key].get_comissions(wallets=True)['withdrawal'])
        withdrawal_commission += wallets_settings.get_withdrawal_commission(key)
        commissions[key] = display_decimal(withdrawal_commission)

    template = bot.get_template(messages.wallets_start_message)
    mess = template.render(commissions=commissions)
    keyboard = keyboards.wallets_menu

    bot.send_message(client, mess, reply_markup=keyboard)


def balance(bot, client):
    btc_wallet, _ = Wallet.objects.get_or_create(
        crypt=CryptSettings.objects.get(name='BTC'),
        client=client
    )
    btc_balance = display_decimal(btc_wallet.balance)
    btc_rub_balance = round(float(btc_wallet.balance) * wallets['BTC'].get_course())

    ltc_wallet, _ = Wallet.objects.get_or_create(
        crypt=CryptSettings.objects.get(name='LTC'),
        client=client
    )
    ltc_balance = display_decimal(ltc_wallet.balance)
    ltc_rub_balance = round(float(ltc_wallet.balance) * wallets['LTC'].get_course())

    xmr_wallet, _ = Wallet.objects.get_or_create(
        crypt=CryptSettings.objects.get(name='XMR'),
        client=client
    )
    xmr_balance = display_decimal(xmr_wallet.balance)
    xmr_rub_balance = round(float(xmr_wallet.balance) * wallets['XMR'].get_course())

    usdt_wallet, _ = Wallet.objects.get_or_create(
        crypt=CryptSettings.objects.get(name='USDT'),
        client=client
    )
    usdt_balance = display_decimal(usdt_wallet.balance)
    usdt_rub_balance = round(float(usdt_wallet.balance) * wallets['USDT'].get_course())

    template = bot.get_template(messages.wallets_balance_message)
    mess = template.render(
        btc_balance=btc_balance,
        btc_rub_balance=btc_rub_balance,

        ltc_balance=ltc_balance,
        ltc_rub_balance=ltc_rub_balance,

        xmr_balance=xmr_balance,
        xmr_rub_balance=xmr_rub_balance,

        usdt_balance=usdt_balance
    )
    keyboard = keyboards.wallets_menu

    bot.send_message(client, mess, reply_markup=keyboard)


def deposit(bot, client):
    mess = messages.choice_deposit_crypt_message
    keyboard = keyboards.deposit_menu

    client.set_state('choice_deposit_crypt')
    bot.send_message(client, mess, reply_markup=keyboard)


def choice_deposit_crypt(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return start(bot, client)

    try:
        crypt = CryptSettings.objects.get(name=message.text)
        wallets_settings = WalletsSettings.objects.first()

        if not wallets_settings.get_deposit_available(crypt.name):
            template = bot.get_template(messages.deposit_unavailable_message)
            mess = template.render(crypt=crypt.name)
            keyboard = keyboards.wallets_menu

            client.clear_state()
            bot.send_message(client, mess, reply_markup=keyboard)
            return

    except CryptSettings.DoesNotExist:
        mess = messages.incorrect_value_message
        keyboard = keyboards.deposit_menu

        bot.send_message(client, mess, reply_markup=keyboard)
        return

    wallet, _ = Wallet.objects.get_or_create(crypt=crypt, client=client)

    if wallet.address is None:
        wallet.address = wallets[crypt.name].get_address(wallets=True)
        wallet.save()

    min_deposit = wallets[crypt.name].get_min_deposit(wallets=True)
    has_min_deposit = min_deposit > 0.0

    deposit_commission = float(wallets[crypt.name].get_comissions(wallets=True)['deposit'])
    has_deposit_commission = deposit_commission > 0.0

    template = bot.get_template(messages.deposit_message)
    mess = template.render(
        address=wallet.address,
        crypt=crypt.name,
        min_deposit=display_decimal(min_deposit),
        has_min_deposit=has_min_deposit,
        deposit_commission=display_decimal(deposit_commission),
        has_deposit_commission=has_deposit_commission
    )
    keyboard = keyboards.get_new_deposit_address_keyboard(crypt.name)

    client.clear_state()
    bot.send_message(client, mess, reply_markup=keyboard)
    bot.send_message(client, '------------------------', reply_markup=keyboards.wallets_menu)


def new_deposit_address(bot, client, call):
    data_crypt = call.data.split('-')[1]

    try:
        crypt = CryptSettings.objects.get(name=data_crypt)
        wallets_settings = WalletsSettings.objects.first()

        if not wallets_settings.get_deposit_available(crypt.name):
            template = bot.get_template(messages.deposit_unavailable_message)
            mess = template.render(crypt=crypt.name)
            keyboard = keyboards.wallets_menu

            client.clear_state()
            bot.send_message(client, mess, reply_markup=keyboard)
            bot.edit_message_reply_markup(client, call.message.id, reply_markup=None)
            return

    except CryptSettings.DoesNotExist:
        mess = messages.incorrect_value_message
        keyboard = keyboards.deposit_menu

        bot.send_message(client, mess, reply_markup=keyboard)
        bot.edit_message_reply_markup(client, call.message.id, reply_markup=None)
        return

    wallet, _ = Wallet.objects.get_or_create(crypt=crypt, client=client)

    address = wallets[crypt.name].get_address(wallets=True)
    wallet.address = address
    wallet.save()

    min_deposit = wallets[crypt.name].get_min_deposit(wallets=True)
    has_min_deposit = min_deposit > 0.0

    deposit_commission = float(wallets[crypt.name].get_comissions(wallets=True)['deposit'])
    has_deposit_commission = deposit_commission > 0.0

    template = bot.get_template(messages.deposit_message)
    mess = template.render(
        address=wallet.address,
        crypt=crypt.name,
        min_deposit=display_decimal(min_deposit),
        has_min_deposit=has_min_deposit,
        deposit_commission=display_decimal(deposit_commission),
        has_deposit_commission=has_deposit_commission
    )
    keyboard = keyboards.get_new_deposit_address_keyboard(crypt.name)

    client.clear_state()
    bot.edit_message_text(client, call.message.id, mess, reply_markup=None)

def history(bot, client):
    mess = messages.choice_history_crypt_message
    keyboard = keyboards.history_crypt_menu

    client.set_state('choice_history_crypt')
    bot.send_message(client, mess, reply_markup=keyboard)


def choice_history_crypt(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return start(bot, client)

    try:
        crypt = CryptSettings.objects.get(name=message.text)

    except CryptSettings.DoesNotExist:
        mess = messages.incorrect_value_message
        keyboard = keyboards.deposit_menu

        bot.send_message(client, mess, reply_markup=keyboard)
        return

    client.meta['wallets_history'] = {'crypt': crypt.name}
    client.save()

    mess = messages.choice_history_category_message
    keyboard = keyboards.history_category_menu

    client.set_state('choice_history_category')
    bot.send_message(client, mess, reply_markup=keyboard)


def choice_history_category(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return start(bot, client)

    match message.text:
        case 'Вывод':
            category = 'withdrawal'

        case 'Депозит':
            category = 'deposit'

        case _:
            mess = messages.incorrect_value_message
            keyboard = keyboards.history_category_menu

            bot.send_message(client, mess, reply_markup=keyboard)
            return

    crypt = CryptSettings.objects.get(name=client.meta['wallets_history']['crypt'])
    wallet, _ = Wallet.objects.get_or_create(crypt=crypt, client=client)
    transactions = WalletTransaction.objects.filter(wallet=wallet, category=category).order_by('-id')[:20]

    if transactions.count() == 0:
        mess = messages.empty_history_message

    else:
        template = bot.get_template(messages.history_message)
        mess = template.render(transactions=transactions)

    keyboard = keyboards.wallets_menu

    client.clear_state()
    bot.send_message(client, mess, reply_markup=keyboard)


def withdrawal(bot, client):
    mess = messages.choice_withdrawal_crypt_message
    keyboard = keyboards.withdrawal_crypt_menu

    client.set_state('choice_withdrawal_crypt')
    bot.send_message(client, mess, reply_markup=keyboard)


def choice_withdrawal_crypt(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return start(bot, client)

    try:
        crypt = CryptSettings.objects.get(name=message.text)
        wallets_settings = WalletsSettings.objects.first()

        if not wallets_settings.get_withdrawal_available(crypt.name):
            template = bot.get_template(messages.withdrawal_unavailable_message)
            mess = template.render(crypt=crypt.name)
            keyboard = keyboards.wallets_menu

            client.clear_state()
            bot.send_message(client, mess, reply_markup=keyboard)
            return

    except CryptSettings.DoesNotExist:
        mess = messages.incorrect_value_message
        keyboard = keyboards.withdrawal_crypt_menu

        bot.send_message(client, mess, reply_markup=keyboard)
        return

    client.meta['withdrawal'] = {'crypt': crypt.name}
    client.save()

    mess = messages.get_withdrawal_address_message
    keyboard = keyboards.cancel_button

    client.set_state('get_withdrawal_address')
    bot.send_message(client, mess, reply_markup=keyboard)


def get_withdrawal_address(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return start(bot, client)

    crypt = client.meta['withdrawal']['crypt']
    search_result = re.search(wallets[crypt].address_regex, message.text)

    if not search_result:
        mess = messages.incorrect_value_message
        keyboard = keyboards.cancel_button

        bot.send_message(client, mess, reply_markup=keyboard)
        return

    wallet, _ = Wallet.objects.get_or_create(
        crypt=CryptSettings.objects.get(name=crypt),
        client=client
    )

    if wallet.address == message.text:
        mess = messages.self_address_message
        keyboard = keyboards.cancel_button

        bot.send_message(client, mess, reply_markup=keyboard)
        return

    client.meta['withdrawal']['address'] = message.text
    client.save()

    template = bot.get_template(messages.get_withdrawal_amount_message)
    mess = template.render(crypt=crypt)
    keyboard = keyboards.cancel_button

    client.set_state('get_withdrawal_amount')
    bot.send_message(client, mess, reply_markup=keyboard)


def get_withdrawal_amount(bot, client, message):
    def get_count_after_dot(string):
        if '.' in string or ',' in string:
            index = string.index('.') if '.' in string else string.index(',')
            substring = string[index+1:]
            return len(substring)

        return 0

    if message.text == '❌ Отмена':
        client.clear_state()
        return start(bot, client)

    try:
        amount = float(message.text.replace(',', '.'))

    except ValueError:
        mess = messages.incorrect_value_message
        keyboard = keyboards.cancel_button

        bot.send_message(client, mess, reply_markup=keyboard)
        return

    crypt = CryptSettings.objects.get(name=client.meta['withdrawal']['crypt'])

    amount_places = get_count_after_dot(message.text)
    max_amount_places = 6 if crypt.name == 'USDT' else 8

    if amount_places > max_amount_places:
        template = bot.get_template(messages.max_amount_places_message)
        mess = template.render(max_amount_places=max_amount_places)
        keyboard = keyboards.cancel_button

        bot.send_message(client, mess, reply_markup=keyboard)
        return

    min_withdrawal = wallets[crypt.name].get_min_withdrawal(wallets=True)

    if amount < min_withdrawal:
        template = bot.get_template(messages.min_withdrawal_amount_message)
        mess = template.render(amount=display_decimal(min_withdrawal), crypt=crypt.name)
        keyboard = keyboards.cancel_button

        bot.send_message(client, mess, reply_markup=keyboard)
        return

    wallets_settings = WalletsSettings.objects.first()
    withdrawal_commission = Decimal(wallets[crypt.name].get_comissions(wallets=True)['withdrawal'])
    withdrawal_commission += wallets_settings.get_withdrawal_commission(crypt.name)

    client.meta['withdrawal']['amount'] = amount
    client.meta['withdrawal']['commission'] = float(withdrawal_commission)
    client.save()

    template = bot.get_template(messages.confirm_withdrawal_message)
    mess = template.render(
        amount=display_decimal(amount),
        crypt=crypt.name,
        address=client.meta['withdrawal']['address'],
        full_amount=display_decimal(Decimal(str(amount)) + withdrawal_commission)
    )
    keyboard = keyboards.confirm_withdrawal_menu

    client.set_state('confirm_withdrawal')
    bot.send_message(client, mess, reply_markup=keyboard)


def confirm_withdrawal(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        return start(bot, client)

    elif message.text == '✅ Подтвердить':
        crypt = CryptSettings.objects.get(name=client.meta['withdrawal']['crypt'])
        wallets_settings = WalletsSettings.objects.first()
        wallet, _ = Wallet.objects.get_or_create(crypt=crypt, client=client)

        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(id=wallet.id)

            withdrawal_commission = Decimal(str(client.meta['withdrawal']['commission']))
            real_withdrawal_commission = Decimal(wallets[crypt.name].get_comissions(wallets=True)['withdrawal'])

            if real_withdrawal_commission > withdrawal_commission:
                mess = messages.withdrawal_error_message
                keyboard = keyboards.wallets_menu

                client.clear_state()
                bot.send_message(client, mess, reply_markup=keyboard)
                return

            amount = Decimal(str(client.meta['withdrawal']['amount']))

            if (amount + withdrawal_commission) > wallet.balance:
                mess = messages.insufficient_funds_message
                keyboard = keyboards.wallets_menu

                client.clear_state()
                bot.send_message(client, mess, reply_markup=keyboard)
                return

            receiver_wallet = Wallet.objects.filter(crypt=crypt, address=client.meta['withdrawal']['address'])

            if receiver_wallet.exists():
                receiver_wallet = receiver_wallet.first()

                transaction = WalletTransaction.objects.create(
                    wallet=wallet,
                    category='withdrawal',
                    internal=True,
                    tx_id=uuid.uuid4(),
                    address=receiver_wallet.address,
                    amount=-amount,
                    commission=withdrawal_commission,
                    provider_commission=Decimal('0')
                )
                wallet.update_balance(transaction.amount - transaction.full_commission)
                wallets_settings.update_profit(crypt.name, transaction.commission)

                receive_transaction = WalletTransaction.objects.create(
                    wallet=receiver_wallet,
                    category='deposit',
                    internal=True,
                    tx_id=uuid.uuid4(),
                    address=receiver_wallet.address,
                    amount=amount,
                    commission=Decimal('0'),
                    provider_commission=Decimal('0')
                )
                receiver_wallet.update_balance(receive_transaction.amount)

            else:
                withdrawal = wallets[crypt.name].send_crypt(
                    client.meta['withdrawal']['address'],
                    display_decimal(amount),
                    fee=0,
                    wallets=True
                )

                if type(withdrawal) != dict:
                    mess = messages.withdrawal_error_message
                    keyboard = keyboards.wallets_menu

                    client.clear_state()
                    bot.send_message(client, mess, reply_markup=keyboard)
                    return

                transaction = WalletTransaction.objects.create(
                    wallet=wallet,
                    category='withdrawal',
                    tx_id=withdrawal['txid'],
                    explorer_link=withdrawal['tx_link'],
                    address=withdrawal['address'],
                    amount=-amount,
                    commission=withdrawal_commission - Decimal(withdrawal['fee']),
                    provider_commission=Decimal(withdrawal['fee'])
                )
                wallet.update_balance(transaction.amount - transaction.full_commission)
                wallets_settings.update_profit(crypt.name, transaction.commission)

        template = bot.get_template(messages.success_withdrawal_message)
        mess = template.render(explorer_link=transaction.explorer_link)
        keyboard = keyboards.wallets_menu

        client.clear_state()
        bot.send_message(client, mess, reply_markup=keyboard)

        if transaction.internal:
            template = bot.get_template(messages.success_deposit_message)
            mess = template.render(transaction=receive_transaction)

            bot.send_message(receiver_wallet.client, mess)

    else:
        mess = messages.incorrect_value_message
        keyboard = keyboards.confirm_withdrawal_menu

        bot.send_message(client, mess, reply_markup=keyboard)
        return


def deposit_action(bot, client):
    bot.send_message(client, 'Выберите способ пополнения кошелька:', reply_markup=keyboards.deposit_action_menu)


def deposit_from_exchange(bot, client):
    if Order.objects.filter(client=client, status='pending').exists():
        bot.send_message(client, '⛔️ Сначала должен завершиться предыдущий обмен', reply_markup=keyboards.start_menu)
        return
    
    client.meta['deposit_order'] = True
    client.save()

    bot.send_message(client, 'Выберите валюту', reply_markup=keyboards.buy_crypt_menu)

