start_message = '⬇ Выберите меню ниже:'

chat_message = '''
<a href='{{settings.chat_link}}'>💰Чат💰</a>
'''

channel_message = '''
<a href='{{settings.channel_news}}'>💰Канал новостей💰</a>
'''

office_message = '''
Ваш уникальный ID: <code>{{client.tg_id}}</code>
Количество обменов: <b>{{client.count}}</b>
Количество рефералов: <b>{{client.ref_count}}</b>
Реферальный счет: <b>{{client.ref_profit}} RUB</b>

<code>Приводи активных рефералов и зарабтывай!</code>

Твоя <b>реферальная ссылка:</b>
{{ref_link}}
'''

min_promocode_treshold_value = '''
⛔️ Для использования <b>данного промокода</b> совершите <b>{{order_count}}</b> обмен
'''

max_used_promocode_message = '''
Извини, этот промокод уже использован максимальное количество раз 🙂 
Попробуй в следующий раз быть более оперативным
'''

expiration_promocode_message = '''
⛔️ Срок действия промокода истек
'''

get_promocode_message = 'Введите промокод ниже:'
incorrect_promocode_message = '⛔️ Некорректный промокод, попробуйте еще раз'
promocode_already_used_message = '⚠️ Промокод уже был активирован'
activate_promocode_message = '''
Промокод <b>{{promo.name}}</b> активирован ✅

Доступная скидка на обмен: <b>{{promo.discount}}</b> {% if promo.in_fiat %}RUB{% else %}%{% endif %}
'''

contacts_message = '⬇ Наши контакты'

sell_crypt_message = 'Для продажи криптовалюты пишите @{{support}}'

crypt_not_available_message = '''
⚙️ Извините, обмен <b>{{crypt}}</b> временно недоступен по одной из двух причин:

📶 Сеть <b>{{crypt}}</b> перегружена;
💵 Обменный пункт пополняет резервы;
'''
get_value_message = '''
💰 Введи нужную сумму в <b>{{crypt}}</b>{% if crypt != 'USDT' %} или в <b>RUB</b>{% endif %}:

{% if client.get_active_promocodes()|length > 0 %}
🏷 Выбери доступный промокод
{% endif %}
'''

sell_crypt_not_available_message = '''
⚙️ Извините, продажа <b>{{crypt}}</b> временно недоступна
🧑🏼‍💻 Обратитесь к @{{settings.support_contact}} для продажи в ручном режиме
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
<b>ВВОДИ СУММУ В {{crypt}}:</b>
<i>пример: 0.001</i>
'''

choice_sell_payment_method = '''
За продажу <b>{{order_sell.crypt_value}} {{crypt}}</b> ты получишь <b>{{order_sell.pay_value_with_percent}} ₽</b> 
\nСпособ зачисления: <b>{{order_sell.payment_method_name}}</b>
'''

get_requisites_sell_payment_method = '''
⚙️ Введи реквизиты для получения выплаты за продажу
\n<b>{{payment_type}}:</b>
'''

sell_order_message = '''
К оплате: <b>{{order_sell.crypt_value}} {{crypt}}</b>
Получишь: <b>{{order_sell.pay_value_with_percent}} RUB</b>
Реквизиты: <b>{{requisites}}</b>
'''

order_sell_info_message = '''
Заявка #{{order_sell.order_id}}

⚠️ <b>ВАЖНО ПЕРЕВОДИТЬ ТОЧНУЮ СУММУ УКАЗАННУЮ, БОТОМ</b>

👇👇👇👇👇👇👇👇

Переведите <code>{{order_sell.crypt_value}}</code> {{order_sell.crypt}} на <code>{{order_sell.address}}</code>

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

incorrect_value_message = '⛔️ Некорректное значение, попробуйте еще раз'
# min_value_message = 'Минимальное значение: <b>{{rub_value}} RUB</b> или <b>{{crypt_value}} {{crypt}}</b>'
min_value_message = '''
Минимальное значение: <b>{{rub_value}} RUB</b> или <b>{{crypt_value}} {{crypt}}</b>
Для продолжения сделки на указанную сумму обратитесь к оператору @{{support}}, либо увеличьте сумму и продолжите обмен в боте с минимальной комиссией.
'''
many_digits_message = '⛔️ Некорректное значение, допустимо не больше <b>8</b> знаков после запятой'

choice_payment_method_message = '''
{% if order.bonus %}❗️<b>Это бонусный обмен</b>❗️{% endif %}
{% if order.payment_method %}\nСпособ оплаты: <b>{{order.payment_method_name}}</b>{% endif %}
Получите: {% if order.crypt == 'USDT' %}<b>{{order.crypt_value}} {{order.crypt}} ({{order.rub_value|int}} ₽)</b>{% else %}<b>{{order.crypt_value}} {{order.crypt}}</b>{% endif %}{% if order.cashback %}\nКешбэк: <b>{{order.cashback}} ₽</b>{% endif %}{% if order.promocode %}\nПромокод: <b>{{order.promocode}}</b>{% endif %}{% if order.discount %}\nСкидка: <b>{{order.discount}} ₽</b>{% endif %}
{% if order.discount > 0 or order.cashback > 0 %}К оплате: <s>{{order.real_pay_value}} ₽</s> -> <code>{{order.pay_value}}</code> ₽{% else %}К оплате: <code>{{order.pay_value}}</code> ₽{% endif %}

<u>Выберите способ оплаты</u>⬇️
'''

bonus_order_message = '''
{% set remaning_count = order_count - left_count %}
{% set bonus_progress = '🟢' * remaning_count + '⚪' * (left_count)%}

Сделок до бонусного обмена: <b>{{left_count}}</b>\n{{bonus_progress}}
'''

choiced_payment_method_message = '''
{% if payment_type == 'sbp' %}
Способ оплаты: 📱 Система быстрых платежей
{% else %}
Способ оплаты: 💳 Visa/Mastercard/MIR
{% endif %}
'''
get_address_message = 'Введите свой <b>{{crypt}}</b> адрес:'
incorrect_address_message = '⛔️ Некорректный <b>{{crypt}}</b> адрес, попробуйте еще раз'

order_info_message = '''
Банк получателя: <b>{{order.payment_method_name}}</b>
Реквизиты: <code>{{order.requisites}}</code>
Сумма к оплате: <b>{{order.pay_value}} RUB</b>
К получению: <b>{{order.crypt_value}} {{order.crypt}}</b>
На кошелек: <b>{{order.address}}</b>

🔺 Внимание: Переводить точную сумму!
🔺 После оплаты нажмите
"✅ Я оплатил"
{% if timer %}
⏱ На оплату даётся <b>{{timer}}</b> мин!
{% endif %}
'''
order_info_message_with_pay_link = '''
Сумма к оплате: <b>{{order.pay_value}} RUB</b>
К получению: <b>{{order.crypt_value}} {{order.crypt}}</b>
На кошелек: <b>{{order.address}}</b>

Для оплаты перейдите по ссылке:
{{pay_link}}

<i>Данный способ оплаты это временное решение нашего платежного провайдера, перейдя по ссылке Вы выбираете способ оплаты (номер карты / СБП) и получаете номер для перевода. Ваши средства в безопасности.</i>

🔺 Внимание: Переводить точную сумму!
🔺 После оплаты нажмите
"✅ Я оплатил"
{% if timer %}
⏱ На оплату даётся <b>{{timer}}</b> мин!
{% endif %}
'''
cancel_order_message = '⛔️ Заявка отменена'

wait_message = '''
🗳 Заявка: №<code>{{order.order_id}}</code>

⏳ Статус: обрабатывается...
💵 Сумма внесения: <b>{{order.pay_value}} RUB</b>

🔺 Пожалуйста, отправьте чек или скриншот оплаты — это поможет быстрее найти ваш платёж.

❗️ Если этого не сделать - заявка может быть отменена, время обработки может значительно увеличится. Спасибо за понимание!
'''

order_message = '''
<code>{{order.client.tg_id}}</code>
{% if order.bonus_order %}❗️Бонусная заявка❗️{% endif %}
✉️ Заявка #<b>{{order.order_id}}</b>{% if order.label %}\n👨‍💻 ID процессинга: <code>{{order.label}}</code>{% endif %}{% if 'payok_id' in order.payload %}\n🟡 Payok id: <code>{{order.payload.payok_id}}</code>{% endif %}
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
'''

not_enough_ref_profit_message = '''
⛔️ Минимальная сумма вывода <b>{{min_ref_withdrawal}} RUB</b>
💳 Ваш счет: <b>{{ref_profit}} RUB</b>
'''

create_withdrawal_message = '''
✅ Заявка на вывод #{{withdrawal.requests_id}} успешно создана!

📞 Предоставьте реквизиты для выплаты @{{settings.boss_contact}}
'''

buy_many_crypt_message = '''
Для покупки криптовалюты пишите пишите @{{support}}
'''

get_luck_message = 'Вы испытали удачу 🤑! Теперь ваша скидка составляет <b>{{client.discount}} RUB</b>'
time_error_message = '⛔️⏰ С момента последнего вращения не прошли сутки, попробуйте позже'
already_have_discount_message = '⚠️ Вы не использовали предыдущую скидку в размере <b>{{client.discount}} RUB</b>'

choice_calc_crypt_message = 'Выберите валюту'
get_calc_value_message = 'Введите значение для <b>{{crypt}}</b> в <b>РУБЛЯХ</b>'
calc_result_message = '''
<code>{{rub_value}}</code> рублей
это по курсу <code>{{crypt_value}}</code> {{crypt}}
'''

accept_withdrawal_message = 'Вы уверены что хотите вывести <b>{{client.ref_profit}} RUB</b> на карту и <u>обнулить</u> свой счёт?'

wallets_start_message = '''
🔐 Это твой персональный крипто – кошелек. 

🔺принимай и отправляй переводы 
🔺храни криптовалюту
🔺создавай уникальные адреса

Анонимно и безопасно.

⚠️За отправку с кошелька взимаются следующие комиссии:

BTC - {{commissions['BTC']}}
LTC - {{commissions['LTC']}}
XMR - {{commissions['XMR']}}
USDT - {{commissions['USDT']}} 
'''

wallets_balance_message = '''
<b>BTC:</b> <code>{{btc_balance}}</code> ~ {{btc_rub_balance}} RUB
<b>LTC:</b> <code>{{ltc_balance}}</code> ~ {{ltc_rub_balance}} RUB
<b>XMR:</b> <code>{{xmr_balance}}</code> ~ {{xmr_rub_balance}} RUB
<b>USDT:</b> <code>{{usdt_balance}}</code> ~ {{usdt_rub_balance}} RUB
'''

choice_deposit_crypt_message = 'Выберите валюту:'
deposit_unavailable_message = '⛔️ Депозит <b>{{crypt}}</b> временно недоступен'
deposit_message = '''
Сеть: <b>{{crypt}}{% if crypt == 'USDT' %}-TRC20{% endif %}</b>
Адрес: <code>{{address}}</code>{% if has_min_deposit %}\nМин. депозит: <b>{{min_deposit}} {{crypt}}</b>{% endif%}{% if has_deposit_commission %}\nКомиссия: <b>{{deposit_commission}} {{crypt}}</b>{% endif %}
'''
success_deposit_message = '''
💸 Зачисление депозита

Сумма: <code>{{transaction.display_amount}}</code> <b>{{transaction.wallet.crypt.name}}</b>
Комиссия: <code>{{transaction.display_full_commission}}</code> <b>{{transaction.wallet.crypt.name}}</b>
'''

choice_history_crypt_message = 'Выберите валюту:'
choice_history_category_message = 'Выберите категорию:'
empty_history_message = 'Транзакции отсутствуют'
history_message = '''
Последние <b>20</b> транзакций:

{% for transaction in transactions %}
Сумма: <code>{{transaction.display_amount}}</code> <b>{{transaction.wallet.crypt.name}}</b>
Комиссия: <code>{{transaction.display_full_commission}}</code> <b>{{transaction.wallet.crypt.name}}</b>{% if transaction.category == 'withdrawal' %}\nАдрес получателя: <code>{{transaction.address}}</code>{% endif %}
Дата создания (по Мск.): {{transaction.created_at.strftime('%d.%m.%Y %H:%M:%S')}}
{% endfor %}
'''

choice_withdrawal_crypt_message = 'Выберите валюту:'
withdrawal_unavailable_message = '⛔️ Вывод <b>{{crypt}}</b> временно недоступен'
get_withdrawal_address_message = 'Введите адрес получателя:'
self_address_message = '⛔️ Нельзя указывать свой адрес в качестве получателя'
get_withdrawal_amount_message = 'Введите сумму вывода в <b>{{crypt}}</b>:'
min_withdrawal_amount_message = '⛔️ Минимальная сумма вывода: <code>{{amount}}</code> <b>{{crypt}}</b>'
max_amount_places_message = '⛔️ Максимальное допустимое кол-во цифр после запятой: <b>{{max_amount_places}}</b>'
confirm_withdrawal_message = '''
🔺Внимание🔺

Сумма вывода: <code>{{amount}}</code> <b>{{crypt}}</b>
Сумма вывода c комиссией: <code>{{full_amount}}</code> <b>{{crypt}}</b>
Адрес получателя: <code>{{address}}</code>
'''
insufficient_funds_message = '⛔️ Недостаточно средств'
withdrawal_error_message = '⛔️ Что-то пошло не так, попробуйте еще раз'
success_withdrawal_message = '''
✅ Успешный вывод
{% if explorer_link %}Ссылка для отслеживания: {{explorer_link}}{% endif %}
'''











