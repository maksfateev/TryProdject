from datetime import datetime

from django.db import models, transaction

from telegram.models import Client, Notification
from general_settings.models import Card, GeneralSettings

# Create your models here.


class CardProxy(Card):
    class Meta:
        proxy = True
        verbose_name = 'Карта'
        verbose_name_plural = 'Карты'


class Trader(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Никнейм')
    client = models.OneToOneField(
        Client,
        on_delete=models.CASCADE,
        related_name='trader',
        verbose_name='Аккаунт'
    )
    balance = models.BigIntegerField(default=0, verbose_name='Баланс')
    received = models.BigIntegerField(default=0, verbose_name='Принято')
    active = models.BooleanField(default=True, verbose_name='Активный')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')

    in_work = models.BooleanField(default=False, verbose_name='В работе')

    class Meta:
        verbose_name = 'Трейдер'
        verbose_name_plural = 'Трейдеры'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.active:
            self.in_work = False

        super().save(*args, **kwargs)


class WorkingShift(models.Model):
    trader = models.ForeignKey(
        Trader,
        on_delete=models.CASCADE,
        related_name='working_shifts',
        verbose_name='Трейдер'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Смена трейдера'
        verbose_name_plural = 'Смены трейдеров'

    def __str__(self):
        return str(self.id)

    @property
    def amount(self):
        _amount = 0
        orders = self.orders.filter(status='confirmed')

        for order in orders:
            _amount += order.changed_amount or order.amount

        return _amount


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', '⚠️ В обработке'),
        ('confirmed', '✅ Подтверждена'),
        ('rejected', '❌ Отменена')
    )

    order_id = models.CharField(max_length=200, unique=True, verbose_name='ID заявки')
    trader = models.ForeignKey(Trader, on_delete=models.CASCADE, verbose_name='Трейдер')
    working_shift = models.ForeignKey(
        WorkingShift,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Смена'
    )

    amount = models.BigIntegerField(verbose_name='Сумма')
    changed_amount = models.BigIntegerField(null=True, blank=True, verbose_name='Измененная сумма')

    bank = models.CharField(max_length=200, verbose_name='Банк')
    cardholder_name = models.CharField(max_length=200, verbose_name='ФИО держателя')
    requisites = models.CharField(max_length=200, verbose_name='Реквизиты')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    changed_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )

    closed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def __str__(self):
        return self.order_id

    def change_amount(self, amount):
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=self.id)

            if order.status == 'pending':
                order.changed_amount = amount
                order.save()

    def reject(self):
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=self.id)

            if order.status == 'pending':
                order.status = 'rejected'
                order.save()

    def confirm(self):
        with transaction.atomic():
            order = Order.objects.select_for_update().get(id=self.id)

            if order.status == 'pending':
                order.status = 'confirmed'
                order.trader.balance -= order.changed_amount or order.amount
                order.trader.received += order.changed_amount or order.amount
                order.trader.save()
                order.save()

                notification = Notification.objects.create(
                    bank=order.bank,
                    notification_type='Пополнение',
                    pay=order.changed_amount or order.amount,
                    balance=0,
                    datetime=datetime.now(),
                    confirmed=True
                )

        if order.status == 'confirmed':
            try:
                from telegram.handler import sms_bot as bot
                
                admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)
                bot.send_message(admin, f'Банк: {notification.bank}\n✅💸 Подтвержденное пополнение {notification.pay} RUB')

            except:
                pass




