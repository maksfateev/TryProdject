import os
from .modules import handlers
from .modules_admin import handlers as handlers_admin
from .bot import Bot
from dotenv import load_dotenv
from .models import Client
from .modules_admin import handlers as handlers_admin
from .modules_trading import handlers as handlers_trading
from general_settings.models import GeneralSettings
from trading.models import Trader
import logging
import traceback

from . import protection

load_dotenv()
bot = Bot(os.getenv('BOT_TOKEN'), 10)
trading_bot = Bot(os.getenv('TRADING_BOT_TOKEN'), 5)

btc_bot = Bot(os.getenv('BTC_BOT_TOKEN'), 1)
ltc_bot = Bot(os.getenv('LTC_BOT_TOKEN'), 1)
xmr_bot = Bot(os.getenv('XMR_BOT_TOKEN'), 1)
usdt_bot = Bot(os.getenv('USDT_BOT_TOKEN'), 1)
sms_bot = Bot(os.getenv('SMS_BOT_TOKEN'), 1)
sell_bot = Bot(os.getenv('SELL_BOT_TOKEN'), 1)

logger = logging.getLogger('BOT')

@bot.message_handler(commands=['start'])
@protection.protect
def start(message, client=None):
    if message.chat.id < 0:
        return

    try:
        data = message.text.split()
        if len(data) == 2 and client.state:
                return

        if client.tg_id == GeneralSettings.objects.first().admin_tg_id:
            action = handlers_admin.message_handlers['/start']
        else:
            action = handlers.message_handlers['/start']

        logger.info({'tg_id': message.chat.id, 'message': message.text})
        action(bot, client, message)
    except Exception as e:
        logger.error({'message': message.text, 'error': traceback.format_exc()})

@bot.message_handler(content_types=['text'], func=lambda message: not Client.get_or_create(bot, message).state)
@protection.protect
def text(message, client=None):
    if message.chat.id < 0:
        return

    try:
        if client.tg_id == GeneralSettings.objects.first().admin_tg_id:
            if message.text in handlers_admin.message_handlers:
                action = handlers_admin.message_handlers[message.text]
            else:
                action = handlers_admin.message_handlers['unknown_command']
                return action(bot, client, message)
        else:
            if message.text in handlers.message_handlers:
                action = handlers.message_handlers[message.text]
            else:
                action = handlers.message_handlers['/start']
                return action(bot, client)

        logger.info({'tg_id': message.chat.id, 'message': message.text})
        action(bot, client)
    except Exception as e:
        logger.error({'message': message.text, 'error': traceback.format_exc()})

@bot.message_handler(content_types=['text'], func=lambda message: Client.get_or_create(bot, message).state)
@protection.protect
def state_text(message, client=None):
    if message.chat.id < 0:
        return

    try:
        if client.tg_id == GeneralSettings.objects.first().admin_tg_id:
            if client.state and client.state != 'passes_captcha':
                action = handlers_admin.state_handlers[client.state]
            else:
                action = handlers_admin.message_handlers['/start']
                return action(bot, client)
        else:
            if client.state and client.state != 'passes_captcha':
                action = handlers.state_handlers[client.state]
            else:
                action = handlers.message_handlers['/start']
                return action(bot, client)

        logger.info({'tg_id': message.chat.id, 'message': message.text, 'state': client.state})
        action(bot, client, message)
    except Exception as e:
        print(traceback.format_exc())
        logger.error({'tg_id': message.chat.id, 'message': message.text, 'state': client.state, 'error': traceback.format_exc()})
        
@bot.message_handler(content_types=['document', 'photo'], func=lambda message: Client.get_or_create(bot, message).state)
def handle_document(message):
    client = Client.get_or_create(bot, message)

    if message.chat.id < 0:
        return
    try:
        if client.state and client.state != 'passes_captcha':
            action = handlers.state_handlers[client.state]
        else:
            action = handlers.message_handlers['/start']
            return action(bot, client)
        
        logger.info({'tg_id': message.chat.id, 'message': 'document/photo', 'state': client.state})
        action(bot, client, message)

    except Exception as e:
        logger.error({'tg_id': message.chat.id, 'message': 'document/photo', 'state': client.state, 'error': traceback.format_exc()})

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message.chat.id < 0:
        return

    try:
        client = Client.get_or_create(bot, call.message)
        if client.ban:
            return
            
        data = call.data.split('-')
        if client.tg_id == GeneralSettings.objects.first().admin_tg_id:
            action = handlers_admin.callback_handlers[data[0]]
        else:
            action = handlers.callback_handlers[data[0]]

        logger.info({'tg_id': call.message.chat.id, 'call': call.data})
        action(bot, client, call)
    except Exception as e:
        logger.error({'tg_id': call.message.chat.id, 'call': call.data, 'error': traceback.format_exc()})


@trading_bot.message_handler(commands=['start'])
def start_trading_bot(message):
    if message.chat.id < 0:
        return

    try:
        client = Client.get_or_create(trading_bot, message)
        trader = Trader.objects.filter(client=client).first()

        if trader is None:
            return trading_bot.send_message(client, '⚠️ Дождитесь регистрации в системе')

        elif not trader.active:
            return

        action = handlers_trading.message_handlers['/start']
        logger.info({'tg_id': message.chat.id, 'message': message.text})
        action(trading_bot, client)

    except Exception as e:
        logger.error({'message': message.text, 'error': traceback.format_exc()})


@trading_bot.message_handler(content_types=['text'], func=lambda message: not Client.get_or_create(trading_bot, message).state)
def text_trading_bot(message):
    if message.chat.id < 0:
        return

    try:
        client = Client.get_or_create(trading_bot, message)
        trader = Trader.objects.filter(client=client).first()

        if trader is None or not trader.active:
            return

        if message.text in handlers_trading.message_handlers:
            action = handlers_trading.message_handlers[message.text]

        else:
            action = handlers_trading.message_handlers['unknown_command']
            return action(trading_bot, client, message)

        logger.info({'tg_id': message.chat.id, 'message': message.text})
        action(trading_bot, client)

    except Exception as e:
        logger.error({'message': message.text, 'error': traceback.format_exc()})


@trading_bot.message_handler(content_types=['text'], func=lambda message: Client.get_or_create(trading_bot, message).state)
def state_text_trading_bot(message):
    if message.chat.id < 0:
        return

    try:
        client = Client.get_or_create(trading_bot, message)
        trader = Trader.objects.filter(client=client).first()

        if trader is None or not trader.active:
            return

        if client.state in handlers_trading.state_handlers:
            action = handlers_trading.state_handlers[client.state]

        else:
            action = handlers_trading.message_handlers['/start']
            return action(trading_bot, client)

        logger.info({'tg_id': message.chat.id, 'message': message.text, 'state': client.state})
        action(trading_bot, client, message)

    except Exception as e:
        logger.error({'tg_id': message.chat.id, 'message': message.text, 'state': client.state, 'error': traceback.format_exc()})


@trading_bot.callback_query_handler(func=lambda call: True)
def callback_trading_bot(call):
    if call.message.chat.id < 0:
        return

    try:
        client = Client.get_or_create(trading_bot, call.message)
        trader = Trader.objects.filter(client=client).first()

        if trader is None or not trader.active:
            return

        data = call.data.split('-')
        action = handlers_trading.callback_handlers[data[0]]
        logger.info({'tg_id': call.message.chat.id, 'call': call.data})
        action(trading_bot, client, call)

    except Exception as e:
        logger.error({'tg_id': call.message.chat.id, 'call': call.data, 'error': traceback.format_exc()})


@btc_bot.callback_query_handler(func=lambda call: True)
def callback_btc_bot(call):
    if call.message.chat.id < 0:
        return

    try:
        client = Client.get_or_create(btc_bot, call.message)
        if client.ban:
            return
            
        data = call.data.split('-')
        if client.tg_id == GeneralSettings.objects.first().admin_tg_id:
            action = handlers_admin.callback_handlers[data[0]]
            logger.info({'tg_id': call.message.chat.id, 'call': call.data})
            action(btc_bot, client, call)

    except Exception as e:
        logger.error({'tg_id': call.message.chat.id, 'call': call.data, 'error': traceback.format_exc()})

@ltc_bot.callback_query_handler(func=lambda call: True)
def callback_ltc_bot(call):
    if call.message.chat.id < 0:
        return

    try:
        client = Client.get_or_create(ltc_bot, call.message)
        if client.ban:
            return
            
        data = call.data.split('-')
        if client.tg_id == GeneralSettings.objects.first().admin_tg_id:
            action = handlers_admin.callback_handlers[data[0]]
            logger.info({'tg_id': call.message.chat.id, 'call': call.data})
            action(ltc_bot, client, call)
            
    except Exception as e:
        logger.error({'tg_id': call.message.chat.id, 'call': call.data, 'error': traceback.format_exc()})

@xmr_bot.callback_query_handler(func=lambda call: True)
def callback_xmr_bot(call):
    if call.message.chat.id < 0:
        return

    try:
        client = Client.get_or_create(xmr_bot, call.message)
        if client.ban:
            return
            
        data = call.data.split('-')
        if client.tg_id == GeneralSettings.objects.first().admin_tg_id:
            action = handlers_admin.callback_handlers[data[0]]
            logger.info({'tg_id': call.message.chat.id, 'call': call.data})
            action(xmr_bot, client, call)
            
    except Exception as e:
        logger.error({'tg_id': call.message.chat.id, 'call': call.data, 'error': traceback.format_exc()})

@usdt_bot.callback_query_handler(func=lambda call: True)
def callback_usdt_bot(call):
    if call.message.chat.id < 0:
        return

    try:
        client = Client.get_or_create(usdt_bot, call.message)
        if client.ban:
            return
            
        data = call.data.split('-')
        if client.tg_id == GeneralSettings.objects.first().admin_tg_id:
            action = handlers_admin.callback_handlers[data[0]]
            logger.info({'tg_id': call.message.chat.id, 'call': call.data})
            action(usdt_bot, client, call)
            
    except Exception as e:
        logger.error({'tg_id': call.message.chat.id, 'call': call.data, 'error': traceback.format_exc()})
        
@sell_bot.callback_query_handler(func=lambda call: True)
def callback_sell_bot(call):
    if call.message.chat.id < 0:
        return

    try:
        client = Client.get_or_create(sell_bot, call.message)
        if client.ban:
            return

        data = call.data.split('-')
        if client.tg_id == GeneralSettings.objects.first().admin_tg_id:
            action = handlers_admin.callback_handlers[data[0]]
            logger.info({'tg_id': call.message.chat.id, 'call': call.data})
            action(sell_bot, client, call)

    except Exception as e:
        logger.error({'tg_id': call.message.chat.id, 'call': call.data, 'error': traceback.format_exc()})



