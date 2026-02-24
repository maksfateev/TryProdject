from . import keyboards
from telegram.models import Order, Review
from general_settings.models import GeneralSettings


def get_review(bot, client, call):
    data = call.data.split('-')
    order = Order.objects.get(order_id=data[1])

    if Review.objects.filter(order=order).exists():
        bot.answer_callback_query(call.id, '⛔️ Вы уже оставили отзыв по данному обмену!', show_alert=True)
        return
    
    client.set_state('get_review_text')
    client.meta['review'] = {'order': order.order_id}
    client.save()

    bot.send_message(client, 'Напиши текст отзыва', reply_markup=keyboards.cancel_button)


def get_review_text(bot, client, message):
    if message.text == '❌ Отмена':
        client.clear_state()
        client.update_meta()
        bot.send_message(client, '------', reply_markup=keyboards.start_menu)
        return
    
    order = Order.objects.get(order_id=client.meta['review']['order'])
    review = Review.objects.create(order=order, client=client, text=message.text)

    client.clear_state()
    client.update_meta()

    bot.send_message(client, 'Спасибо за отзыв!', reply_markup=keyboards.start_menu)
    settings = GeneralSettings.objects.first()

    if settings and settings.reviews_tg_id is not None:
        bot.send_review(client.tg_id, message.message_id)
