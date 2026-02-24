import telebot

start_menu = telebot.types.ReplyKeyboardMarkup(True)
start_menu.row('BTC📤', 'LTC📤', 'XMR📤', 'USDT📤')
start_menu.row('Получить реквизиты', '💳 Балансы')
start_menu.row('Заявка на продажу')
start_menu.row('Баланс', 'Функционал')
start_menu.row('🎞', '🧮', '💳', '💸')

get_reqs_menu = telebot.types.ReplyKeyboardMarkup(True)
get_reqs_menu.row('Номер карты', 'СБП')
get_reqs_menu.row('❌ Отмена')

cancel_button = telebot.types.ReplyKeyboardMarkup(True).row('❌ Отмена')

accept_send_menu = telebot.types.ReplyKeyboardMarkup(True)
accept_send_menu.row('✅ Да', '❌ Нет')

choice_crypt_menu = telebot.types.ReplyKeyboardMarkup(True)
choice_crypt_menu.row('BTC', 'LTC', 'XMR', 'USDT')
choice_crypt_menu.row('Меню 🏠')

get_percent_menu = telebot.types.ReplyKeyboardMarkup(True)
get_percent_menu.row('16%', '17%', '18%', '19%')
get_percent_menu.row('20%', '21%', '22%', '23%')
get_percent_menu.row('24%', '25%', '26%', '27%')
get_percent_menu.row('28%', '29%', '30%', 'RUB')
get_percent_menu.row('Меню 🏠')

menu_button = telebot.types.ReplyKeyboardMarkup(True).row('Меню 🏠')

history_menu = telebot.types.ReplyKeyboardMarkup(True)
history_menu.row('ПРИНЯТО', 'ОТПРАВЛЕНО')
history_menu.row('Меню 🏠')

functional_menu = telebot.types.ReplyKeyboardMarkup(True)
functional_menu.row('Alfateam', 'Secrett', 'Infinitypay')
functional_menu.row('Pspware', 'Merchant001', 'Extasypay')
functional_menu.row('Bitzone', 'Wellbit')
functional_menu.row('КАССА', 'Откуп')
functional_menu.row('Вкл/выкл ночь', 'Назначить оператора')
functional_menu.row('Блок', 'Сделать вывод')
functional_menu.row('⚙️ Настройки', '☠️ Бан')
functional_menu.row('Перенос реферала', 'Перенос статы')
functional_menu.row('Меню 🏠')

sell_crypt_menu = telebot.types.ReplyKeyboardMarkup(True)
sell_crypt_menu.row('Продать BTC', 'Продать LTC')
sell_crypt_menu.row('⬅️ Назад')

order_sell_menu = telebot.types.ReplyKeyboardMarkup(True)
order_sell_menu.row('✅ Продолжить', '❌ Отмена')

xpay_menu = telebot.types.ReplyKeyboardMarkup(True)
xpay_menu.row('Изменить баланс Xpay', 'Обнулить баланс Xpay')
xpay_menu.row('Меню 🏠')

alfateam_menu = telebot.types.ReplyKeyboardMarkup(True)
alfateam_menu.row('Изменить баланс Alfateam', 'Обнулить баланс Alfateam')
alfateam_menu.row('Меню 🏠')

pspware_menu = telebot.types.ReplyKeyboardMarkup(True)
pspware_menu.row('Изменить баланс Pspware', 'Обнулить баланс Pspware')
pspware_menu.row('Меню 🏠')

bridgepay_menu = telebot.types.ReplyKeyboardMarkup(True)
bridgepay_menu.row('Изменить баланс Bridgepay', 'Обнулить баланс Bridgepay')
bridgepay_menu.row('Меню 🏠')

bridgepay_tj_menu = telebot.types.ReplyKeyboardMarkup(True)
bridgepay_tj_menu.row('Изменить баланс Bridgepay TJ', 'Обнулить баланс Bridgepay TJ')
bridgepay_tj_menu.row('Меню 🏠')

secrett_menu = telebot.types.ReplyKeyboardMarkup(True)
secrett_menu.row('Изменить баланс Secrett', 'Обнулить баланс Secrett')
secrett_menu.row('Меню 🏠')

merchant001_menu = telebot.types.ReplyKeyboardMarkup(True)
merchant001_menu.row('Изменить баланс Merchant001', 'Обнулить баланс Merchant001')
merchant001_menu.row('Меню 🏠')

bitzone_menu = telebot.types.ReplyKeyboardMarkup(True)
bitzone_menu.row('Изменить баланс Bitzone', 'Обнулить баланс Bitzone')
bitzone_menu.row('Меню 🏠')

wellbit_menu = telebot.types.ReplyKeyboardMarkup(True)
wellbit_menu.row('Изменить баланс Wellbit', 'Обнулить баланс Wellbit')
wellbit_menu.row('Меню 🏠')

extasypay_menu = telebot.types.ReplyKeyboardMarkup(True)
extasypay_menu.row('Изменить баланс Extasypay', 'Обнулить баланс Extasypay')
extasypay_menu.row('Меню 🏠')

infinitypay_menu = telebot.types.ReplyKeyboardMarkup(True)
infinitypay_menu.row('Изменить баланс Infinitypay', 'Обнулить баланс Infinitypay')
infinitypay_menu.row('Меню 🏠')

vita_menu = telebot.types.ReplyKeyboardMarkup(True)
vita_menu.row('Изменить баланс Vita', 'Обнулить баланс Vita')
vita_menu.row('Меню 🏠')

ban_menu = telebot.types.ReplyKeyboardMarkup(True)
ban_menu.row('❌ Забанить', '❇️ Разбанить')
ban_menu.row('Меню 🏠')

settings_menu = telebot.types.InlineKeyboardMarkup()
settings_menu.row(
	telebot.types.InlineKeyboardButton(text='BTC', callback_data=f'settings-btc'),
	telebot.types.InlineKeyboardButton(text='LTC', callback_data=f'settings-ltc'),
	telebot.types.InlineKeyboardButton(text='XMR', callback_data=f'settings-xmr'),
	telebot.types.InlineKeyboardButton(text='USDT', callback_data=f'settings-usdt'),
)
settings_menu.row(
	telebot.types.InlineKeyboardButton(text='АВТО', callback_data=f'settings-auto'),
	telebot.types.InlineKeyboardButton(text='ПРИЕМКА', callback_data=f'settings-sell')
)

get_fee_menu = telebot.types.ReplyKeyboardMarkup(True)
get_fee_menu.row('♻️ АВТО', '❌ Отмена')

ignore_button = telebot.types.ReplyKeyboardMarkup(True).row('❌ Не учитывать')

cashier_menu = telebot.types.ReplyKeyboardMarkup(True)
cashier_menu.row('✅ Да', '❌ Нет')

withdrawal_menu = telebot.types.ReplyKeyboardMarkup(True)
withdrawal_menu.row('Зарплата')
withdrawal_menu.row('❌ Отмена')
