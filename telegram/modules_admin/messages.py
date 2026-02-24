start_message = '------'
order_message = '''
<code>{{order.client.tg_id}}</code>
{% if order.bonus_order %}❗️Бонусная заявка❗️{% endif %}
✉️ Заявка #<b>{{order.order_id}}</b>{% if order.label %}\n👨‍💻 ID процессинга: <code>{{order.label}}</code> ({{order.provider}}){% endif %}{% if 'payok_id' in order.payload %}\n🟡 Payok id: <code>{{order.payload.payok_id}}</code>{% endif %}
👨‍🔧 <a href="tg://user?id={{order.client.tg_id}}">{% if order.client.username %}{{order.client.username}}{% else %}Аноним{% endif %}</a> (<a href="http://194.58.109.169/admin/telegram/client/{{order.client.id}}/change/">{{order.client.tg_id}}</a>)
🧮 Кол-во обменов: <b>{{order.client.count}}</b>{% if order.promocode %}\n🏷 Промокод: <b>{{order.promocode}}</b>{% endif %}
💰 Закинул: <b>{{order.pay_value}} RUB</b> на <code>{{order.requisites}}</code> ({{order.payment_method}})
🌐 Адрес: <a href="https://blockchair.com/en/{% if order.crypt == 'BTC' %}bitcoin{% else %}litecoin{% endif %}/address/{{order.address}}">{{order.address}}</a>
💵 Хочет: <b>{{order.crypt_value}} {{order.crypt}}</b> это <b>{{order.rub_value}} RUB</b>
🚦 Статус: <b>{{order.get_status_display()}}{% if order.status == 'error' %}: {{order.error}}{% endif %}</b>
💸 Оплата: {% if order.notification %}❇️ Найдена{% else %}⛔️ Не найдена{% endif %}
🎁 Скидка - <b>{{order.discount}}</b> RUB
    - Промокод: <b>{{order.discount_info['promocode']}}</b> RUB
    - Бонусная заявка: <b>{{order.discount_info['bonus_discount']}}</b> RUB
    - Рулетка: <b>{{order.discount_info['lucky']}}</b> RUB
    - Кешбек: <b>{{order.discount_info['cashback']}}</b> RUB
⌛️ Истекает в <b>{{order.expired_at}}</b>
{% if auto_handler and order.status == 'pending' %}
🕹 Работает <b>АВТОМАТ</b> 🕹
{% endif %}
{% if order.tx_link %}
{{order.tx_link}}
<b>{{("%.8f"|format(order.crypt_value)).rstrip("0")}} {{order.crypt}}</b> + <b>{{("%.8f"|format(order.fee)).rstrip("0")}} {{order.crypt}}</b>
Примерно: <b>{{order.rub_value}} RUB</b> и <b>{{order.fee_rub}} RUB</b> (комиссия сети)
{% endif %}
'''

reject_order_message = '''
😕 Упс...
🚫 Заявка №<code>{{order.order_id}}</code> отклонена
'''

review_message = '''
Будем благодарны, если вы оставите свой отзыв!
'''

confirm_order_message = '''
🔺Благодарим за обмен!
<b>{{order.crypt_value}} {{order.crypt}}</b> отправлено на указанный Вами адрес: <code>{{order.address}}</code>

🔺 В случае возникновения проблем, напишите: @{{support}}.
🔺 Ожидайте подтверждения транзакции.

{{order.tx_link}}
'''

balance_message = '''
BTC address: <code>{{btc_address}}</code>
BTC balance: <b>{{btc_balance}}</b>
RUB BTC balance: <b>{{btc_rub_balance}}</b>

LTC address: <code>{{ltc_address}}</code>
LTC balance: <b>{{ltc_balance}}</b>
RUB LTC balance: <b>{{ltc_rub_balance}}</b>

XMR address: <code>{{xmr_address}}</code>
XMR balance: <b>{{xmr_balance}}</b>
RUB XMR balance: <b>{{xmr_rub_balance}}</b>

USDT address: <code>{{usdt_address}}</code>
USDT balance: <b>{{usdt_balance}}</b>
RUB USDT balance: <b>{{usdt_rub_balance}}</b>
'''

get_address_message = '🎫 ВВЕДИТЕ АДРЕС <b>{{crypt}}</b> КОШЕЛЬКА'
incorrect_address_message = '⛔️ Некорректный <b>{{crypt}}</b> адрес'

get_value_message = '🛒 Введите колличество 💰 <b>{{crypt}}</b> для отправки'
incorrect_value_message = '⛔️ Некорректное значение <b>{{crypt}}</b>, попробуйте еще раз.'


accept_send_message = '''
‼️Внимание ‼️

Вы действительно хотите отправить <b>{{send.crypt_value}} {{send.crypt}}</b> ~ <b>{{send.rub_value}} RUB</b> на <code>{{send.address}}</code> ?
'''
error_send_message = '''
🆘 Ошибка при отправке транзакции:

<b>{{error}}</b>
'''

success_send_message = '''
✅ Успешная отправка:
{{transaction.tx_link}}

Отправлено: <b>{{transaction.crypt_value}} {{transaction.crypt}} ({{transaction.rub_value}} RUB)</b>
Комиссия сети: <b>{{("%.8f"|format(transaction.fee)).rstrip("0")}} {{transaction.crypt}} ({{transaction.fee_rub}} RUB)</b>
Итого: <b>{{total_rub}} RUB</b>
'''

get_pay_value_message = '''
💸 <b>Укажи, сколько ты получил за эту отправку</b>
'''
incorrect_pay_value_message = '⛔️ Некорректное значение, попробуйте еще раз'

choice_crypt_message = 'Выберите валюту'
get_percent_message = 'Выберите процент'
get_calc_rub_value_message = 'Введите значение для <b>{{calculate.crypt}}</b> в РУБЛЯХ'
get_calc_value_message = 'Введите значение в <b>{{calculate.crypt}}</b>'
incorrect_calc_value_message = '⛔️ Некорректное значение, попробуйте еще раз'
result_rub_message = '''
<b>{{result}} {{calculate.crypt}}</b>
это по курсу <b>{{value}} RUB</b>
'''
result_message = '''
этo <b>{{result}} RUB</b> (+<b>{{percent}}%</b>)
и <b>{{real_value}} RUB</b> без %
'''

choice_history_type_message = 'Выбери историю'
empty_history_message = '😢 Нет транзакций'
history_list_message = '''
{% for tx in txs %}
<i>{{tx.time}}</i>
{% if tx.crypt == 'BTC' %}
<b>{{tx.amount}} {{tx.crypt}}</b> ({{tx.rub_amount}} ₽) на <a href="https://blockchair.com/en/bitcoin/address/{{tx.address}}">{{tx.address}}</a>
{% elif tx.crypt == 'LTC' %}
<b>{{tx.amount}} {{tx.crypt}}</b> ({{tx.rub_amount}} ₽) на <a href="https://blockchair.com/en/litecoin/address/{{tx.address}}">{{tx.address}}</a>
{% elif tx.crypt == 'XMR' %}
<b>{{tx.amount}} {{tx.crypt}}</b> ({{tx.rub_amount}} ₽) на <code>{{tx.address}}</code>
{% elif tx.crypt == 'USDT' %}
<b>{{tx.amount}} {{tx.crypt}}</b> ({{tx.rub_amount}} ₽) на <a href="https://tronscan.org/#/address/{{tx.address}}">{{tx.address}}</a>
{% endif %}
{% endfor %}
'''

choice_action_message = 'Выберите действие'
get_ban_id_message = 'Введите ID клиента, которого хотите забанить'
get_unban_id_message = 'Введите ID клиента, которого хотите разбанить'
incorrect_id_message = '⛔️ Некорректный ID, попробуйте еще раз'
user_banned_message = '☠️ Клиент <code>{{tg_id}}</code> забанен!'
user_unbanned_message = '❇️ Клиент <code>{{tg_id}}</code> разбанен!'

start_settings_message = 'Выберите нужный раздел'
settings_crypt_message = '''
Настройки <b>{{settings.name}}</b>

Статус: {% if settings.available %}✅ВКЛ{% else %}❌ВЫКЛ{% endif %}
Комиссия сети: {{fee}} s/pB {% if settings.auto_fee %}<b>АВТО</b>{% endif %}
Комиссия RUB: {{settings.get_comission()}} RUB
'''
settings_auto_message = '''
Настройки <b>АВТО</b>

Статус: {% if auto_handler %}✅ВКЛ{% else %}❌ВЫКЛ{% endif %}
'''

settings_sell_message = '''
Настройки <b>ПРИЕМКА</b>

Статус: {% if on %}✅ВКЛ{% else %}❌ВЫКЛ{% endif %}
'''

settings_xmr_message = '''
Настройки <b>XMR</b>

Статус: {% if settings.available %}✅ВКЛ{% else %}❌ВЫКЛ{% endif %}
'''
settings_usdt_message = '''
Настройки <b>USDT</b>

Статус: {% if settings.available %}✅ВКЛ{% else %}❌ВЫКЛ{% endif %}
'''
get_fee_message = 'Введите комиссию для <b>{{crypt}}</b> в формате s/pB'
set_auto_fee_message = 'Для <b>{{crypt}}</b> установлена автоматическая комиссия'
set_fee_message = 'Для <b>{{crypt}}</b> установлена комиссия в размере <b>{{fee}} s/pB</b>'

card_message = '''
Реквизиты сбер: <code>{{card.card_number}}</code>
Реквизиты доп. метода оплаты: <code>{{card.sbp_number}}</code>
'''
change_requisites_message = '''
{% if method == 'card' %}
Укажите новые реквизиты для 💳 <b>{{card.name}}</b>
{% else %}
Укажите новые реквизиты для 📱 <b>{{card.name}} СБП</b>
{% endif %}
'''
changed_requisites_message = '''
{% if method == 'card' %}
✅ Новые реквизиты для 💳 <b>{{card.name}}</b> - <code>{{card.card_number}}</code>
{% else %}
✅ Новые реквизиты для 📱 <b>{{card.name}} СБП</b> - <code>{{card.sbp_number}}</code>
{% endif %}
'''
change_balance_message = 'Укажите новый баланс для <b>{{card.name}}</b>'
changed_balance_message = '✅ Новый баланс для <b>{{card.name}}</b> = <code>{{card.balance}}</code> RUB'
notification_history_message = '''
{% for notification in notifications %}
{{notification.datetime}} <b>{{notification.bank}}</b> {% if notification.notification_type == 'Пополнение' %}{% if notification.confirmed %}✅{% else %}❓{% endif %}{% else %}📲{% endif %}
💸 <b>{{notification.pay}}</b> 💳 = <b>{{notification.balance}}</b>
{% endfor %}
'''

tx_confirmed_message = '''
Транзакция <b>{{order.crypt_value}} {{order.crypt}}</b> подтверждена
'''

get_purchase_pay_value_message = '''
💸❓ Укажи сколько денег ты отдал за <b>{{purchase.crypt_value}} {{purchase.crypt}}</b> = <b>{{purchase.rub_value}} RUB</b>
'''
got_purchase_pay_value_message = '''
✅ <b>{{purchase.crypt_value}} {{purchase.crypt}}</b> = {{purchase.pay_value}} RUB
'''
confirm_purchase_pay_value_message = '''
❗️Стоимость закупки больше реальной стоимости на 10%
❓Уверен, что ввел верную стоимость?
'''

chashier_start_message = '''
‼️ВНИМАНИЕ ‼️

Ты уверен, что хочешь завершить текущую СМЕНУ? ЗАКУПИЛСЯ?
'''
cant_close_cashier_message = '❌ У тебя есть незаполненные закупки'
purchase_cashier_message = '''
⛔️ {{purchase.crypt_value}} {{purchase.crypt}} = {{purchase.rub_value|int}} за {{purchase.pay_value|int}}
потеря|профит = {{purchase.rub_value - purchase.pay_value}} = {{purchase.get_percent()}}%
'''
transaction_cashier_message = '🧑‍💻{{transaction.crypt}} {{transaction.pay_value}} + {{transaction.pay_value - transaction.rub_value}}'
working_shift_info_message = '''
✅ {{working_shift}}{% if working_shift.operator %} - {{working_shift.operator.name}}{% endif %}

грязный профит бота = <b>{{working_shift.orders_profit}} руб</b>
количество обменов бот = <b>{{working_shift.orders_count}}</b>
закинули денег с бота = <b>{{working_shift.orders_turnover}} руб</b>

профит оп = <b>{{working_shift.oper_profit|int}} руб</b> + <b>{{working_shift.oper_purchase_profit}} руб</b>{% if working_shift.oper_salary > 0 %} - <b>{{working_shift.oper_salary}} руб</b>{% endif %} = <b>{{working_shift.oper_profit|int + working_shift.oper_purchase_profit - working_shift.oper_salary}} руб</b>
количество обменов оп = <b>{{working_shift.transactions_count}}</b>
общий оборот (пришло денег с бота и ручника) = <b>{{working_shift.turnover}} руб</b>
Оборот с бота = <b>{{working_shift.orders_turnover}} руб</b>
Оборот с ручника = <b>{{working_shift.transactions_turnover}} руб</b>

Выводы за смену <b>{{working_shift.withdrawal_amount}} руб</b>
{% for withdrawal in working_shift.withdrawals.all() %}<b>{{withdrawal.pay_value|int}} руб</b> - {{withdrawal.purpose}}{% if withdrawal.operator %} ({{withdrawal.operator.name}}){% endif %}\n{% endfor %}
Блоки <b>{{working_shift.duty_amount}} руб</b>
{% for duty in working_shift.debts.all() %}<b>{{duty.amount}} руб</b> @{{duty.client_name}}\n{% endfor %}
бот <b>{{working_shift.orders_count}}</b> ручник <b>{{working_shift.transactions_count}}</b>
бот <b>{{working_shift.orders_profit}} руб</b> + ручник <b>{{working_shift.transactions_profit}}</b> (закупы) <b>{{working_shift.purchases_profit}}</b> = <b>{{working_shift.orders_profit+working_shift.transactions_profit+working_shift.purchases_profit}}</b>

<b>BTC</b>: {{working_shift.volatility('BTC')}}
<b>LTC</b>: {{working_shift.volatility('LTC')}}
'''
working_shift_oper_info_message = '''
Профит: <b>{{working_shift.oper_profit|int + working_shift.oper_purchase_profit}} руб</b>
0.2% от оборота: <b>{{working_shift.oper_turnover_profit}} руб</b>
Вывел: <b>{{working_shift.oper_salary}} руб</b>
Баланс: <b>{{working_shift.oper_balance}} руб</b>
'''
profit_message = '''
бот <b>{{working_shift.orders_profit}} руб</b> + ручник <b>{{working_shift.transactions_profit}}</b> (закупы) <b>{{working_shift.purchases_profit}}</b> = <b>{{working_shift.orders_profit+working_shift.transactions_profit+working_shift.purchases_profit}}</b>
Баланс: <b>{{balance}} руб</b>
'''

tx_confirmed_message = '''
✅ Транзакция <code>{{order.crypt_value}}</code> <b>{{order.crypt}}</b> подтверждена!

🔺https://t.me/{{settings.reviews_contact}}
<b>🔺Заходи в чат, напиши свой честный отзыв и стань участником розыгрыша на 1500 ₽ в LTC!</b>
'''

start_competition_message = '''
<b>ЗАБЕРИ {{competition.amount}}₽ И ПОДПИСКУ TELEGRAM PREMIUM⭐!</b>
<b>Соверши обмен после этого сообщения, и автоматически станешь участником розыгрыша!</b>
{% if competition.from_amount > 0 %}
Учитываются обмены от <code>{{competition.from_amount}}</code>₽
{% endif %}
'''

end_competition_message = '''
<b>У НАС ЕСТЬ ПОБЕДИТЕЛЬ!</b>
<b>Счастливчику отправлено уведомление!</b>
<b>ПРИЗ {{amount}}₽ И ПОДПИСКА TELEGRAM PREMIUM ⭐!</b>
'''

winner_message = '''
ПОЗДРАВЛЯЕМ, ЧЕМПИОН!
Ты победил в нашем конкурсе!! Для получения приза свяжись с @{{settings.boss_contact}}
'''

incorrect_bill_message = '''
⛔️ Некорректный чек, попробуй еще раз!

Например:
Чек <b>1000</b> за <b>1200</b>
Закуп чек <b>29000</b> за <b>30000</b>
'''

send_bill_message = '🟣 <b>Чек</b> <code>{{bill.pay_value|int}}</code> + <code>{{bill.profit|int}}</code>'
purchase_bill_message = '⛔️🟣 <code>{{bill.profit|int}}</code> <b>закуп</b> на <code>{{bill.rub_value|int}}</code>'

accept_withdrawal_message = '✅ Вывод заполнен'
withdrawal_message_info = '''
💳 Вывод <b>{{withdrawal.pay_value|int}} RUB</b> ({{withdrawal.purpose}})
'''
withdrawal_salary_message_info = '''
💳 Вывод <b>{{withdrawal.pay_value|int}} RUB</b> ({{withdrawal.purpose}})
💰 Баланс: <b>{{balance|int}} RUB</b>
'''

operator_already_selected_message = '⚠️ Для текущей смены уже назначен оператор: {{operator.name}}'
select_operator_message = 'Выбери оператора для текущей смены'
selected_operator_message = '✅ Для текущей смены назначен оператор: {{operator.name}}'

duty_info = '😿 Блок <b>{{duty.amount}} RUB</b> @{{duty.client_name}}'

order_sell_message = '''
<code>{{order_sell.client.tg_id}}</code>
✉️ Заявка #<b>{{order_sell.order_id}}</b>
👨‍🔧 <a href="tg://user?id={{order_sell.client.tg_id}}">{% if order_sell.client.username %}{{order_sell.client.username}}{% else %}Аноним{% endif %}</a>
💰 Отправил: <b>{{("%.8f"|format(order_sell.crypt_value)).rstrip("0")}} {{order_sell.crypt}}</b>
🌐 Адрес: <a href="https://blockchair.com/en/{% if order_sell.crypt == 'BTC' %}bitcoin{% else %}litecoin{% endif %}/address/{{order_sell.address}}">{{order_sell.address}}</a>
💵 К выплате: <b>{{order_sell.pay_value_with_percent|int}} RUB</b>
💳 Реквизиты: {{order_sell.requisites}}
💸 Статус: <b>{{status}}</b>
'''

order_sell_recalculate_message = '''
<code>{{order_sell.client.tg_id}}</code>
✉️ Заявка #<b>{{order_sell.order_id}}</b>
👨‍🔧 <a href="tg://user?id={{order_sell.client.tg_id}}">{% if order_sell.client.username %}{{order_sell.client.username}}{% else %}Аноним{% endif %}</a>
💰 Отправил: <b>{{("%.8f"|format(order_sell.recalculated_crypt_value|float)).rstrip("0")}} {{order_sell.crypt}}</b>
🌐 Адрес: <a href="https://blockchair.com/en/{% if order_sell.crypt == 'BTC' %}bitcoin{% else %}litecoin{% endif %}/address/{{order_sell.address}}">{{order_sell.address}}</a>
💵 К выплате: <b>{{order_sell.recalculated_pay_value_with_percent|int}} RUB</b>
💳 Реквизиты: {{order_sell.requisites}}
💸 Статус: <b>{{status}}</b>
'''

confirm_sell_order_message = '''
Транзакция подтверждена!
В ближайшее время Вам будет отправлено {% if order_sell.recalculated_pay_value_with_percent %}<s>{{order_sell.pay_value_with_percent|int}} RUB</s> <b>{{order_sell.recalculated_pay_value_with_percent|int}} RUB</b>{% else %}<b>{{order_sell.pay_value_with_percent|int}} RUB</b>{% endif %} на указанные реквизиты <b>{{order_sell.requisites}}</b>

В случае возникновения проблем, пишите в нашу поддержку: @{{support}}.
'''

completed_sell_order_message = '''
Спасибо за обмен!
Отправили {% if order_sell.recalculated_pay_value_with_percent %}<b>{{order_sell.recalculated_pay_value_with_percent|int}} RUB</b>{% else %}<b>{{order_sell.pay_value_with_percent|int}} RUB</b>{% endif %} на указанные вами реквизиты <b>{{order_sell.requisites}}</b>
'''

reject_sell_order_message = '''
😕 Упс...
🚫 Заявка №<code>{{order_sell.order_id}}</code> просрочена
'''

sell_crypt_not_available_message = '''
⚙️ Извините, продажа <b>{{crypt}}</b> временно недоступна
🧑🏼‍💻 Обратитесь к @{{settings.support_contact}} или @{{settings.support2_contact}} для продажи в ручном режиме
'''

sell_crypt_rub_valuer_error = '''
⛔️ Введите сумму в <b>{{crypt}}</b>
'''

sell_crypt_input_sbp_error = '''
⛔️ Номер телефона должен содержать <b>11 цифр</b>.
\nПопробуй ввести номер телефона еще раз.
'''

sell_crypt_input_card_error = '''
⛔️ Номер карты должен содержать <b>16 цифр</b>.
\nПопробуй ввести номер карты еще раз.
'''

get_sell_value_message = '''
👇🏼 <b>ВВОДИ СУММУ В {{crypt}}:</b>
<i>пример: 0.001</i>
'''

get_tg_id_message = '''
👇🏼 Введи <b>tg_id</b> пользователя
'''

choice_sell_payment_method = '''
За продажу <b>{{("%.8f"|format(order_sell.crypt_value)).rstrip("0")}} {{crypt}}</b> ты получишь <b>{{order_sell.pay_value_with_percent}} ₽</b> 
\nСпособ зачисления: <b>{{order_sell.payment_method_name}}</b>
'''

get_requisites_sell_payment_method = '''
⚙️ Введи реквизиты для получения выплаты за продажу
\n<b>{{payment_type}}:</b>
'''

sell_order_message = '''
К оплате: <b>{{("%.8f"|format(order_sell.crypt_value)).rstrip("0")}} {{crypt}}</b>
Получишь: <b>{{order_sell.pay_value_with_percent}} RUB</b>
Реквизиты: <b>{{requisites}}</b>
'''

order_sell_info_message = '''
Заявка #{{order_sell.order_id}}
⚠️ <b>ВАЖНО ПЕРЕВОДИТЬ ТОЧНУЮ СУММУ УКАЗАННУЮ, БОТОМ</b>
👇👇👇👇👇👇👇👇
Переведите <code>{{("%.8f"|format(order_sell.crypt_value)).rstrip("0")}}</code> {{order_sell.crypt}} на <code>{{order_sell.address}}</code>
👆👆👆👆👆👆👆👆
⚠️ <b>На перевод дается {{time}} мин.</b>
💳 Средства будут зачислены после 1 подтверждения
'''
# \n\n<b>РЕКВИЗИТЫ ДЛЯ ПЕРЕВОДА {{order_sell.crypt_value}} {{crypt}}</b>
# \n👇👇👇👇👇👇👇👇
# \n<b>{{address}}</b>
status_sell_order_message = '''
'''

order_sell_message_info = '''
<code>{{order_sell.client.tg_id}}</code>
✉️ Заявка на продажу #<b>{{order_sell.order_id}}</b>
👨‍🔧 <a href="tg://user?id={{order_sell.client.tg_id}}">{% if order_sell.client.username %}{{order_sell.client.username}}{% else %}Аноним{% endif %}</a> (<a href="http://194.58.109.169/admin/telegram/client/{{order_sell.client.id}}/change/">{{order_sell.client.tg_id}}</a>)
💰 Продает: <b>{{("%.8f"|format(order_sell.crypt_value)).rstrip("0")}} {{order_sell.crypt}}</b>
🌐 Адрес: <a href="https://blockchair.com/en/{% if order_sell.crypt == 'BTC' %}bitcoin{% else %}litecoin{% endif %}/address/{{order_sell.address}}">{{order_sell.address}}</a>
💵 Хочет получить: <b>{{order_sell.pay_value_with_percent}} RUB</b> на {{order_sell.requisites}} {{order_sell.payment_method}}
💸 Статус: <b>{{status}}{% if order_sell.status == 'error' %}: {{order_sell.error}}{% endif %}</b>{% if order_sell.updated_datetime %}\n⌚️ Время изменения: {{order_sell.updated_datetime.strftime('%Y-%m-%d %H:%M:%S')}}{% endif %}
'''

order_sell_get_bank_message = '''
🎫 Укажите банк
'''

client_not_exist_message = '''
⛔️ Клиента с tg_id - <b>{{tg_id}}</b> не существует! Попробуйте еще раз!
'''

incorrect_tg_id_message = '''
⛔️ Не корректный tg_id. Попробуйте еще раз!
'''

many_digits_message = '⛔️ Некорректное значение, допустимо не больше <b>8</b> знаков после запятой'

min_value_message = '''
Минимальное значение: <b>{{rub_value}} RUB</b> или <b>{{crypt_value}} {{crypt}}</b>
Для продолжения сделки на указанную сумму обратитесь к оператору @{{support}}, либо увеличьте сумму и продолжите обмен в боте с минимальной комиссией.
'''

get_trader_name = 'Как зовут трейдера?'
get_trading_purchase_amount_message = 'Какую сумму отправил трейдер?'
get_trading_purchase_percent_message = 'Сколько % получил трейдер за эту сумму?'
trading_purchase_message = '''
⚠️🧑🏼‍💻 Закуп от трейдера <b>{{trader}}</b>
потеря|профит = {{bill.profit|int}} = {{percent}}%
'''

provider_balances_message = '''
🅰️ Alfateam: {{payment_method.alfateam_balance}} руб.
🅱 Bitzone: {{payment_method.bitzone_balance}} руб.
🅴 Extasypay: {{payment_method.extasypay_balance}} руб.
Ⓜ️ Merchant001: {{payment_method.merchant001_balance}} руб.
💲 Secrett: {{payment_method.secrett_balance}} руб.
🅿️ Pspware: {{payment_method.pspware_balance}} руб.
〰️ Wellbit: {{payment_method.wellbit_balance}} руб.
🄸 Infinitypay: {{payment_method.infinitypay_balance}} руб.
🅥 Vita: {{payment_method.vita_balance}} руб.
'''