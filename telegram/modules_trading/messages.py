start_message = '------'


get_requisites_bank_message = 'Введите название банка'
get_requisites_cardholder_message = 'Введите ФИО держателя карты'
get_requisites_card_number_message = 'Введите номер карты'
get_requisites_sbp_number_message = 'Введите номер СБП'


card_message = '''
<b>💳 Информация по карте</b>

Банк: <b>{{card.bank}}</b>
ФИО держателя: <b>{{card.cardholder_name}}</b>
Номер карты: <code>{{card.card_number}}</code>
Номер СБП: <code>{{card.phone_number}}</code>
Статус: <b>{{card.get_status_display()}}</b>
'''


delete_requisite_message = 'Удалить карту?'


order_message = '''
✉️ Заявка #<b>{{order.order_id}}</b>
💸 Сумма: {% if order.changed_amount %}<s><b>{{order.amount}} RUB</b></s> <b>{{order.changed_amount}} RUB</b>{% else %}<b>{{order.amount}} RUB</b>{% endif %}
🏦 Банк: <b>{{order.bank}}</b>
👷🏻‍♂️ ФИО держателя: <b>{{order.cardholder_name}}</b>
💳 Реквизиты: <code>{{order.requisites}}</code>
🚦 Статус: <b>{{order.get_status_display()}}</b>
'''

orders_message = '''
{% for order in orders %}
✉️ Заявка #<b>{{order.order_id}}</b>
💸 Сумма: {% if order.changed_amount %}<s><b>{{order.amount}} RUB</b></s> <b>{{order.changed_amount}} RUB</b>{% else %}<b>{{order.amount}} RUB</b>{% endif %}
🏦 Банк: <b>{{order.bank}}</b>
👷🏻‍♂️ ФИО держателя: <b>{{order.cardholder_name}}</b>
💳 Реквизиты: <code>{{order.requisites}}</code>
🚦 Статус: <b>{{order.get_status_display()}}</b>
{% endfor %}
'''


get_new_order_amount_message = 'Введите новую сумму'
incorrect_amount_message = '⛔️ Некорректное значение'


accept_close_working_shift_message = 'Вы уверены, что хотите закрыть смену?'
working_shift_message = 'Оборот за смену: <b>{{working_shift.amount}} RUB</b>'
