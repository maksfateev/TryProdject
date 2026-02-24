from . import messages, keyboards
from general_settings.models import GeneralSettings
from wallets import XMRWallet

static_path = 'telegram/static/img/'


def start(bot, client, message=None):
    client.clear_state()
    client.update_meta()
    
    settings = GeneralSettings.objects.first()
    template = bot.get_template(messages.start_message)
    mess = template.render(support=settings.support_contact)
    keyboard = keyboards.start_menu

    # image = open(static_path + 'start.jpg', 'rb')
    # bot.send_photo(client, image, caption=mess, reply_markup=keyboard)
    bot.send_message(client, mess, reply_markup=keyboard)

def unknown_command(bot, client, message):
    bot.delete_message(client, message.message_id)

def get_chat(bot, client):
    settings = GeneralSettings.objects.first()
    template = bot.get_template(messages.chat_message)
    mess = template.render(settings=settings)
    bot.send_message(client, mess, reply_markup=None)

def get_channel(bot, client):
    settings = GeneralSettings.objects.first()
    template = bot.get_template(messages.channel_message)
    mess = template.render(settings=settings)
    bot.send_message(client, mess, reply_markup=None)
