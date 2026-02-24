from django.db import models
from wallets import BTCWallet, LTCWallet, XMRWallet, USDTWallet, display_decimal
from django.conf import settings

from telegram import models as tg_models
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.contrib.auth import get_user_model

from datetime import datetime

import re

import logging

# Create your models here.
wallets = {
    'BTC': BTCWallet.Wallet,
    'LTC': LTCWallet.Wallet,
    'XMR': XMRWallet.Wallet,
    'USDT': USDTWallet.Wallet
}
factors = {'BTC': 8.8, 'LTC': 1, 'XMR': 0}

logger = logging.getLogger('REQUISITES')


class GeneralSettings(models.Model):
    time_for_payment = models.PositiveIntegerField(verbose_name='Время на оплату', help_text='В минутах')
    time_for_order = models.PositiveIntegerField(verbose_name='Время заявки', help_text='В минутах')
    time_for_sell = models.PositiveIntegerField(verbose_name='Время на перевод крипты', help_text='В минутах',
                                                default=15)
    min_value_first = models.PositiveIntegerField(verbose_name='Мин. сумма на 1 обмен', help_text='В рублях')
    auto_handler = models.BooleanField(verbose_name='Автомат')

    start_happy_time = models.TimeField(verbose_name='Начало счастливого часа', null=True, blank=True)
    end_happy_time = models.TimeField(verbose_name='Конец счастливого часа', null=True, blank=True)
    decrease_commission_value = models.PositiveIntegerField(verbose_name='Уменьшить комиссию на', default=0,
                                                            help_text='В %')
    increase_cashback_value = models.PositiveIntegerField(verbose_name='Увеличить кешбек на', default=0,
                                                            help_text='В %')

    start_unhappy_time = models.TimeField(verbose_name='Начало несчастливого часа', null=True, blank=True)
    end_unhappy_time = models.TimeField(verbose_name='Конец несчастливого часа', null=True, blank=True)
    increase_commission_value = models.PositiveIntegerField(verbose_name='Увеличить комиссию на', default=0,
                                                            help_text='В %')
    decrease_cashback_value = models.PositiveIntegerField(verbose_name='Уменьшить кешбек на', default=0,
                                                            help_text='В %')

    boss_contact = models.CharField(max_length=200, verbose_name='Босс')
    support_contact = models.CharField(max_length=200, verbose_name='Поддержка')
    reviews_contact = models.CharField(max_length=200, verbose_name='Отзывы')
    chat_contact = models.CharField(max_length=200, verbose_name='Чат')
    news_contact = models.CharField(max_length=200, verbose_name='Новости')

    admin_tg_id = models.BigIntegerField(verbose_name='TG ID админа')
    chat_tg_id = models.BigIntegerField(verbose_name='TG ID чата', null=True, blank=True)
    reviews_tg_id = models.BigIntegerField(verbose_name='TG ID канала с отзывами', null=True, blank=True)
    channel_news = models.CharField(max_length=200, default='', verbose_name='Сылка на канал новостей')
    chat_link = models.CharField(max_length=200, default='', verbose_name='Сылка на чат')

    cmc_api_key1 = models.CharField(verbose_name='Ключ CoinMarketCap 1', null=True, blank=True, max_length=200)
    cmc_api_key2 = models.CharField(verbose_name='Ключ CoinMarketCap 2', null=True, blank=True, max_length=200)
    cmc_api_key3 = models.CharField(verbose_name='Ключ CoinMarketCap 3', null=True, blank=True, max_length=200)
    cmc_api_key4 = models.CharField(verbose_name='Ключ CoinMarketCap 4', null=True, blank=True, max_length=200)

    first_discount = models.PositiveIntegerField(
        verbose_name='Скидка на первый обмен',
        default=0,
        help_text='В рублях'
    )
    ref_percent = models.PositiveIntegerField(verbose_name='Процент по реф. программе')
    cashback_percent = models.FloatField(verbose_name='Процент кешбэка')
    min_ref_withdrawal = models.PositiveIntegerField(verbose_name='Минимальная сумма вывода реф. счета')
    cashback_order_count = models.PositiveIntegerField(
        verbose_name='Номер бонусной заявки',
        help_text='Бонусная заявка 50% или со скидкой 200 руб'
    )
    cashback_order_amount = models.PositiveIntegerField(
        verbose_name='Скидка для бонусной заявки',
        default=0,
        help_text='В рублях'
    )

    class Meta:
        verbose_name = 'Основные'
        verbose_name_plural = 'Основные'

        permissions = [
            ('restart_bot', 'Рестарт бота')
        ]

    def __str__(self):
        return 'Основные настройки'


@receiver(pre_save, sender=GeneralSettings, weak=False)
def on_change(sender, instance, **kwargs):
    if instance.id is None:
        return

    try:
        previous = GeneralSettings.objects.get(id=instance.id)
    except:
        return

    qs = tg_models.Client.objects.filter(ref_percent=previous.ref_percent)
    qs.update(ref_percent=instance.ref_percent)


class CryptSellSettings(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')
    percent = models.PositiveIntegerField(verbose_name='Процент', default=10)
    min_value_sell = models.PositiveIntegerField(default=500, verbose_name='Минимальная заявка на продажу',
                                                 help_text='В рублях')
    threshold_value = models.PositiveIntegerField(
        default=800,
        verbose_name='Пороговое значение',
        help_text='Определяет % или фикс в заявке'
    )
    available = models.BooleanField(default=True, verbose_name='Включена')

    class Meta:
        verbose_name = 'Валюта для продажи'
        verbose_name_plural = 'Валюты для продажи'

    def __str__(self):
        return self.name


class CryptSettings(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название')
    percent = models.PositiveIntegerField(verbose_name='Процент', default=0)
    fee = models.PositiveIntegerField(default=0, verbose_name='Комиссия сети', help_text='s/pB')
    auto_fee = models.BooleanField(default=True, verbose_name='Автоматическая комиссия сети')
    min_value = models.PositiveIntegerField(default=500, verbose_name='Минимальная заявка', help_text='В рублях')
    threshold_value = models.PositiveIntegerField(
        default=800,
        verbose_name='Пороговое значение',
        help_text='Определяет % или фикс в заявке'
    )
    fix_comission = models.PositiveIntegerField(default=100, verbose_name='Фиксированная комиссия')

    available = models.BooleanField(default=True, verbose_name='Включена')

    class Meta:
        verbose_name = 'Валюта'
        verbose_name_plural = 'Валюты'

    def __str__(self):
        return self.name

    def is_happy_time(self):
        now = datetime.now().time()
        general_settings = GeneralSettings.objects.first()
        
        start_happy_time = general_settings.start_happy_time
        end_happy_time = general_settings.end_happy_time
        
        if start_happy_time and end_happy_time:
            # Проверка случая, когда интервал не переходит через полночь
            if start_happy_time < end_happy_time:
                return start_happy_time <= now <= end_happy_time
            # Проверка случая, когда интервал переходит через полночь
            else:
                return now >= start_happy_time or now <= end_happy_time
        
        return False

    def is_unhappy_time(self):
        now = datetime.now().time()
        general_settings = GeneralSettings.objects.first()
        
        start_unhappy_time = general_settings.start_unhappy_time
        end_unhappy_time = general_settings.end_unhappy_time
        
        if start_unhappy_time and end_unhappy_time:
            # Проверка случая, когда интервал не переходит через полночь
            if start_unhappy_time < end_unhappy_time:
                return start_unhappy_time <= now <= end_unhappy_time
            # Проверка случая, когда интервал переходит через полночь
            else:
                return now >= start_unhappy_time or now <= end_unhappy_time
        
        return False

    def get_comission(self, course=None):
        match self.name:
            # case 'BTC':
            # 	return 300
            case 'XMR':
                return 75
            case 'USDT':
                return 120
            case _:
                pass

        wallet = wallets[self.name]

        if hasattr(wallet, 'get_comission'):
            comission_crypt = wallet.get_comission()
            course = course or wallet.get_course()
            comission = round(comission_crypt * course)
            print(comission)

            return comission

        factor = factors[self.name]
        if self.auto_fee:
            return round(wallet.get_estimate_fee() * factor)

        return round(self.fee * factor)

    def get_percent(self, value):
        conditions = CryptPercent.objects.filter(crypt=self)
        general_settings = GeneralSettings.objects.first()

        if not conditions.exists():
            cond_0_5000 = CryptPercent.objects.create(crypt=self, from_value=0, to_value=5000, percent=15)
            cond_5000_10000 = CryptPercent.objects.create(crypt=self, from_value=5000, to_value=10000, percent=13)
            cond_10000_30000 = CryptPercent.objects.create(crypt=self, from_value=10000, to_value=30000, percent=11.5)
            cond_30000_50000 = CryptPercent.objects.create(crypt=self, from_value=30000, to_value=50000, percent=10)
            cond_50000 = CryptPercent.objects.create(crypt=self, from_value=50000, percent=9)

        for condition in conditions.order_by('-from_value'):
            from_value = condition.from_value
            to_value = condition.to_value or 9999999999999999999
            if from_value <= value < to_value:
                percent = condition.percent

                if self.is_happy_time():
                    percent -= general_settings.decrease_commission_value

                if self.is_unhappy_time():
                    percent += general_settings.increase_commission_value
                return percent
            
        percent = 12
        if self.is_happy_time():
            percent -= general_settings.decrease_commission_value
        
        if self.is_unhappy_time():
            percent += general_settings.increase_commission_value
            
        return percent


class CryptPercent(models.Model):
    crypt = models.ForeignKey(CryptSettings, on_delete=models.CASCADE)
    from_value = models.PositiveIntegerField(verbose_name='От', help_text='В рублях')
    to_value = models.PositiveIntegerField(verbose_name='До', null=True, blank=True, help_text='В рублях')
    percent = models.FloatField(verbose_name='Процент')

    class Meta:
        verbose_name = ''
        verbose_name_plural = ''

    def __str__(self):
        return ''


class Card(models.Model):
    WORK_STATUS_CHOICES = (
        ('worked_all', 'В работе'),
        ('worked_card', 'В работе (карта)'),
        ('worked_sbp', 'В работе (СБП)'),
    )
    NOTWORK_STATUS_CHOICES = (
        ('ready', 'Готова к работе'),
        ('not_worked', 'Не работает'),
        ('blocked', 'В блоке'),
        ('deleted', 'Удалена')
    )

    STATUS_CHOICES = WORK_STATUS_CHOICES + NOTWORK_STATUS_CHOICES

    # BANK_CHOICES = (
    #     ('Райффайзен', 'Райффайзен'),
    #     ('Тинькофф', 'Тинькофф'),
    #     ('Сбербанк', 'Сбербанк'),
    #     ('Уралсиб', 'Уралсиб'),
    #     ('Росбанк', 'Росбанк'),
    #     ('Альфабанк', 'Альфабанк'),
    #     ('Газпромбанк', 'Газпромбанк'),
    #     ('Акбарс банк', 'Акбарс банк'),
    #     ('Газпром банк', 'Газпром банк'),
    #     ('Мтс банк', 'Мтс банк'),
    #     ('Отп Банк', 'Отп Банк'),
    #     ('Россельхозбанк', 'Россельхозбанк'),
    #     ('УБРиР', 'УБРиР'),
    #     ('Озон банк', 'Озон банк'),
    #     ('Совкомбанк', 'Совкомбанк'),
    #     ('ВТБ', 'ВТБ'),
    #     ('Промсвязьбанк', 'Промсвязьбанк'),
    #     ('МТС Деньги (ЭКСИ Банк)', 'МТС Деньги (ЭКСИ Банк)')
    # )

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Владелец'
    )
    trader = models.ForeignKey(
        'trading.Trader',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Трейдер'
    )

    bank = models.CharField(max_length=200, verbose_name='Банк')
    cardholder_name = models.CharField(max_length=200, verbose_name='ФИО держателя')
    card_number = models.CharField(max_length=100, verbose_name='Номер карты')
    phone_number = models.CharField(max_length=100, verbose_name='Номер телефона')

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='ready',
        verbose_name='Статус'
    )
    count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Карта'
        verbose_name_plural = 'Карты'

    def __str__(self):
        return f'{self.bank}/{self.cardholder_name}'

    @property
    def short_number(self):
        numbers = re.findall(r'\d+', self.card_number)
        numbers = ''.join(numbers)

        return '••' + numbers[-4:]

    short_number.fget.short_description = 'Номер карты'

    def is_worked(self):
        return self.status in [item[0] for item in self.WORK_STATUS_CHOICES]
    
    @property
    def card_owner(self):
        if self.trader is not None:
            return self.trader.name + ' ' + '(трейдер)'

        elif self.user is not None:
            return str(self.user) + ' ' + '(админ)'

        return '-'

    card_owner.fget.short_description = 'Владелец'


@receiver(pre_save, sender=Card, weak=False)
def on_change(sender, instance, **kwargs):
    if instance.id is None:
        return

    try:
        previous = Card.objects.get(id=instance.id)
    except:
        return

    if previous.status != instance.status:
        Card.objects.all().update(count=0)
        instance.count = 0

        if previous.is_worked() and not instance.is_worked():
            stats = CardStats.objects.filter(card=instance, stopped_at=None).last()
            if stats:
                stats.stopped_at = datetime.now()
                stats.save()

        elif not previous.is_worked() and instance.is_worked():
            CardStats.objects.create(card=instance)


class CardStats(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    turnover = models.FloatField(default=0, verbose_name='Пришло на карту')

    started_at = models.DateTimeField(auto_now_add=True, verbose_name='Начало работы')
    stopped_at = models.DateTimeField(null=True, blank=True, verbose_name='Конец работы')

    class Meta:
        verbose_name = 'Статистика карты'
        verbose_name_plural = 'Статистика карты'

        ordering = ['-id']

    def __str__(self):
        return ''


class RequisitesRequest(models.Model):
    provider = models.CharField(max_length=100, verbose_name='Провайдер')
    amount = models.IntegerField(verbose_name='Сумма')
    requisites = models.CharField(max_length=255, null=True, blank=True, verbose_name='Реквизиты')
    success = models.BooleanField(verbose_name='Успешно')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    label = models.CharField(max_length=200, null=True, blank=True)
    request_id = models.CharField(max_length=200, null=True, blank=True)
    tg_id = models.BigIntegerField(null=True, blank=True, verbose_name='TG ID клиента')

    class Meta:
        verbose_name = 'Запрос на выдачу реквизитов'
        verbose_name_plural = 'Запросы на выдачу реквизитов'

    def __str__(self):
        return ''


class PaymentMethod(models.Model):
    PROVIDERS = [
        'macrodroid',
        'secrett',
        'alfateam',
        'pspware',
        'merchant001',
        'bitzone',
        'wellbit',
        'extasypay',
        'infinitypay',
        'vita',
        'collybus'
        'test_provider'
    ]

    ALFA_METHOD_PROVIDER_CHOICES = (
        ('extasypay', 'Extasypay'),
        ('infinitypay', 'Infinitypay'),
        ('merchant001', 'Merchant001'),
        ('pspware', 'Pspware'),
        ('collybus', 'Collybus'),
        ('bitzone', 'Bitzone'),
    )

    OZON_METHOD_PROVIDER_CHOICES = (
        ('extasypay', 'Extasypay'),
        ('infinitypay', 'Infinitypay'),
        ('bitzone', 'Bitzone'),
        ('pspware', 'Pspware'),
    )

    SBER_METHOD_PROVIDER_CHOICES = (
        ('extasypay', 'Extasypay'),
        ('pspware', 'Pspware'),
        ('bitzone', 'Bitzone'),
    )

    CARD_PROVIDER_CHOICES = []

    for provider in PROVIDERS:
        CARD_PROVIDER_CHOICES.append((provider, provider))
    
    CARD_PROVIDER_CHOICES = tuple(CARD_PROVIDER_CHOICES)
    SBP_PROVIDER_CHOICES = CARD_PROVIDER_CHOICES
    
    ADD_METHOD_PROVIDER_CHOICES = (
        ('bridgepay_tj', 'bridgepay TJ'),
    )
    
    # Card settings.
    card_name = models.CharField(max_length=200, verbose_name='Название раздела')
    card_provider = models.CharField(
        max_length=50,
        choices=CARD_PROVIDER_CHOICES,
        default='macrodroid',
        verbose_name='Провайдер'
    )
    card_provider_first_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=CARD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 1'
    )
    card_provider_second_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=CARD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 2'
    )
    card_provider_third_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=CARD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 3'
    )
    card_provider_fourth_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=CARD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 4'
    )
    card_provider_fifth_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=CARD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 5'
    )
    card_provider_sixth_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=CARD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 6'
    )
    card_provider_seventh_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=CARD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 7'
    )
    card_provider_eighth_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=CARD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 8'
    )
    card_description = models.TextField(default="", verbose_name='Описание')
    card_on = models.BooleanField(default=True, verbose_name='Вкл.')

    # Sbp settings.
    sbp_name = models.CharField(max_length=200, verbose_name='Название раздела')
    sbp_provider = models.CharField(
        max_length=50,
        choices=SBP_PROVIDER_CHOICES,
        default='macrodroid',
        verbose_name='Провайдер'
    )
    sbp_provider_first_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=SBP_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 1'
    )
    sbp_provider_second_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=SBP_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 2'
    )
    sbp_provider_third_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=SBP_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 3'
    )
    sbp_provider_fourth_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=SBP_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 4'
    )
    sbp_provider_fifth_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=SBP_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 5'
    )
    sbp_provider_sixth_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=SBP_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 6'
    )
    sbp_provider_seventh_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=SBP_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 7'
    )
    sbp_provider_eighth_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=SBP_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 8'
    )
    sbp_description = models.TextField(default="", verbose_name='Описание')
    sbp_on = models.BooleanField(default=True, verbose_name='Вкл.')

    # Additional method settings.
    add_method_name = models.CharField(max_length=200, default="", verbose_name='Название раздела')
    add_method_provider = models.CharField(
        max_length=50,
        choices=ADD_METHOD_PROVIDER_CHOICES,
        default='bridgepay_tj',
        verbose_name='Провайдер'
    )
    add_method_provider_first_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=ADD_METHOD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 1'
    )
    add_method_provider_second_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=ADD_METHOD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 2'
    )
    add_method_provider_third_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=ADD_METHOD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 3'
    )
    add_method_description = models.TextField(default="", verbose_name='Описание')
    add_method_on = models.BooleanField(default=True, verbose_name='Вкл.')

    alfa_monobank_name = models.CharField(max_length=200, default="", verbose_name='Название раздела')
    alfa_monobank_provider = models.CharField(
        max_length=50,
        choices=ALFA_METHOD_PROVIDER_CHOICES,
        default='extasypay',
        verbose_name='Основной провайдер'
    )
    alfa_monobank_provider_first_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=ALFA_METHOD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 1'
    )
    alfa_monobank_provider_second_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=ALFA_METHOD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 2'
    )
    alfa_monobank_provider_third_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=ALFA_METHOD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 3'
    )
    alfa_monobank_provider_fourth_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=ALFA_METHOD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 4'
    )
    alfa_monobank_provider_fifth_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=ALFA_METHOD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 5'
    )
    alfa_monobank_provider_sixth_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=ALFA_METHOD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 6'
    )
    alfa_monobank_provider_seventh_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=ALFA_METHOD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 7'
    )
    alfa_monobank_description = models.TextField(default="", verbose_name='Описание')
    alfa_monobank_on = models.BooleanField(default=False, verbose_name='Вкл.')

    ozon_monobank_name = models.CharField(max_length=200, default="", verbose_name='Название раздела')
    ozon_monobank_provider = models.CharField(
        max_length=50,
        choices=OZON_METHOD_PROVIDER_CHOICES,
        default='merchant001',
        verbose_name='Основной провайдер'
    )
    ozon_monobank_provider_first_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=OZON_METHOD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 1'
    )
    ozon_monobank_provider_second_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=OZON_METHOD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 2'
    )
    ozon_monobank_provider_third_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=OZON_METHOD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 3'
    )
    ozon_monobank_provider_fourth_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=OZON_METHOD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 4'
    )
    ozon_monobank_provider_fifth_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=OZON_METHOD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 5'
    )
    ozon_monobank_provider_sixth_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=OZON_METHOD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 6'
    )
    ozon_monobank_description = models.TextField(default="", verbose_name='Описание')
    ozon_monobank_on = models.BooleanField(default=False, verbose_name='Вкл.')

    sber_monobank_name = models.CharField(max_length=200, default="", verbose_name='Название раздела')
    sber_monobank_provider = models.CharField(
        max_length=50,
        choices=SBER_METHOD_PROVIDER_CHOICES,
        default='extasypay',
        verbose_name='Основной провайдер'
    )
    sber_monobank_provider_first_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=SBER_METHOD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 1'
    )
    sber_monobank_provider_second_reserve = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=SBER_METHOD_PROVIDER_CHOICES,
        default=None,
        verbose_name='Резервный провайдер 2'
    )
    sber_monobank_description = models.TextField(default="", verbose_name='Описание')
    sber_monobank_on = models.BooleanField(default=False, verbose_name='Вкл.')

    xpay_balance = models.IntegerField(default=0, verbose_name='Баланс Xpay')
    onlypays_balance = models.IntegerField(default=0, verbose_name='Баланс Onlypays')
    bridgepay_balance = models.IntegerField(default=0, verbose_name='Баланс Bridgepay')
    bridgepay_tj_balance = models.IntegerField(default=0, verbose_name='Баланс Bridgepay TJ')
    maxwealth_balance = models.IntegerField(default=0, verbose_name='Баланс Maxwealth')
    secrett_balance = models.IntegerField(default=0, verbose_name='Баланс Secrett')
    alfateam_balance = models.IntegerField(default=0, verbose_name='Баланс AlfaTeam')
    pspware_balance = models.IntegerField(default=0, verbose_name='Баланс PSPWare')
    merchant001_balance = models.IntegerField(default=0, verbose_name='Баланс Merchant001')
    bitzone_balance = models.IntegerField(default=0, verbose_name='Баланс Bitzone')
    wellbit_balance = models.IntegerField(default=0, verbose_name='Баланс Wellbit')
    extasypay_balance = models.IntegerField(default=0, verbose_name='Баланс Extasypay')
    infinitypay_balance = models.IntegerField(default=0, verbose_name='Баланс Infinitypay')
    vita_balance = models.IntegerField(default=0, verbose_name='Баланс Vita')
    collybus_balance = models.IntegerField(default=0, verbose_name='Баланс Collybus')

    class Meta:
        verbose_name = 'Метод оплаты'
        verbose_name_plural = 'Методы оплаты'

    class GetRequisitesException(Exception):
        pass

    class GetRequisitesTimeOut(Exception):
        pass

    def __str__(self):
        return ''

    def macro_link(self):
        return f'{settings.HOST}/telegram/notification/{self.id}/?sms=[notification]'

    macro_link.short_description = 'Ссылка для уведомлений макрос'

    def macro_link1(self):
        return f'{settings.HOST}/telegram/notification/{self.id}/?sms=[sms_message]'

    macro_link1.short_description = 'Ссылка для смс макрос'

    def get_requisites(self, amount, reqs_type, tg_id=None):
        def create_client(provider_name):
            if not provider_name:
                return None
            client = __import__(f'providers.{provider_name}', fromlist=['']).Client()
            if provider_name == 'xpay' and tg_id is not None:
                client.tg_id = tg_id
            return client

        provider = getattr(self, f'{reqs_type}_provider')
        
        if reqs_type == 'alfa_monobank':
            reserve_providers = [
                getattr(self, f'{reqs_type}_provider_first_reserve'),
                getattr(self, f'{reqs_type}_provider_second_reserve'),
                getattr(self, f'{reqs_type}_provider_third_reserve'),
                getattr(self, f'{reqs_type}_provider_fourth_reserve'),
                getattr(self, f'{reqs_type}_provider_fifth_reserve'),
                getattr(self, f'{reqs_type}_provider_sixth_reserve'),
                getattr(self, f'{reqs_type}_provider_seventh_reserve'),
            ]
            
        elif reqs_type == 'sber_monobank':
            reserve_providers = [
                getattr(self, f'{reqs_type}_provider_first_reserve'),
                getattr(self, f'{reqs_type}_provider_second_reserve'),
            ]

        elif reqs_type == 'ozon_monobank':
            reserve_providers = [
                getattr(self, f'{reqs_type}_provider_first_reserve'),
                getattr(self, f'{reqs_type}_provider_second_reserve'),
                getattr(self, f'{reqs_type}_provider_third_reserve'),
                getattr(self, f'{reqs_type}_provider_fourth_reserve'),
                getattr(self, f'{reqs_type}_provider_fifth_reserve'),
                getattr(self, f'{reqs_type}_provider_sixth_reserve'),
            ]

        else:
            reserve_providers = [
                getattr(self, f'{reqs_type}_provider_first_reserve'),
                getattr(self, f'{reqs_type}_provider_second_reserve'),
                getattr(self, f'{reqs_type}_provider_third_reserve'),
                getattr(self, f'{reqs_type}_provider_fourth_reserve'),
                getattr(self, f'{reqs_type}_provider_fifth_reserve'),
                getattr(self, f'{reqs_type}_provider_sixth_reserve'),
                getattr(self, f'{reqs_type}_provider_seventh_reserve'),
                getattr(self, f'{reqs_type}_provider_eighth_reserve'),
            ]

        clients = [create_client(provider)] + [create_client(rp) for rp in reserve_providers]

        for idx, client in enumerate(clients):
            if not client:
                continue

            try:
                if getattr(client, 'name', None) and amount < 3000:
                    continue

                data = client.create_p2p_order(amount, reqs_type)
                data['provider'] = provider if idx == 0 else reserve_providers[idx - 1]
                RequisitesRequest.objects.create(
                    provider=data['provider'],
                    amount=amount,
                    requisites=data['reqs'],
                    success=True,
                    label=data.get('label'),
                    request_id=data.get('request_id'),
                    tg_id=tg_id
                )
                logger.info(f"✅ {data['provider']}")

                return data

            except (client.RequestException, client.TimeOutException):
                RequisitesRequest.objects.create(
                    provider=provider if idx == 0 else reserve_providers[idx - 1],
                    amount=amount,
                    success=False,
                    tg_id=tg_id
                )
                logger.info(f"⛔️ {provider if idx == 0 else reserve_providers[idx - 1]}")

        raise self.GetRequisitesException()

    def clean(self):
        if self.card_provider == self.card_provider_first_reserve or self.card_provider == self.card_provider_second_reserve:
            raise ValidationError("Основной провайдер не может совпадать с резервными провайдерами.")
        if self.card_provider_first_reserve == self.card_provider_second_reserve and self.card_provider_first_reserve is not None:
            raise ValidationError("Резервные провайдеры не могут совпадать.")

        if self.sbp_provider == self.sbp_provider_first_reserve or self.sbp_provider == self.sbp_provider_second_reserve:
            raise ValidationError("Основной провайдер SBP не может совпадать с резервными провайдерами.")
        if self.sbp_provider_first_reserve == self.sbp_provider_second_reserve and self.sbp_provider_first_reserve is not None:
            raise ValidationError("Резервные провайдеры SBP не могут совпадать.")

        if self.add_method_provider == self.add_method_provider_first_reserve or self.add_method_provider == self.add_method_provider_second_reserve:
            raise ValidationError("Основной провайдер доп. метода не может совпадать с резервными провайдерами.")
        if self.add_method_provider_first_reserve == self.add_method_provider_second_reserve and self.add_method_provider_first_reserve is not None:
            raise ValidationError("Резервные провайдеры доп. метода не могут совпадать.")

        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Cashier(models.Model):
    channel = models.BigIntegerField(verbose_name='TG ID канала')
    profit_channel = models.BigIntegerField(null=True, blank=True, verbose_name='Касса чистого профита')
    profit_balance = models.BigIntegerField(default=0, verbose_name='Баланс чистого профита')
    oper_percent = models.PositiveIntegerField(verbose_name='Процент оператора с ручных обменов')

    class Meta:
        verbose_name = 'Касса'
        verbose_name_plural = 'Касса'

    def __str__(self):
        return 'Настройки кассы'

class WalletsSettings(models.Model):
    # BTC.
    btc_deposit_available = models.BooleanField(default=True, verbose_name='Депозит доступен')
    btc_withdrawal_available = models.BooleanField(default=True, verbose_name='Вывод доступен')
    btc_withdrawal_commission = models.DecimalField(
        max_digits=25,
        decimal_places=8,
        default=Decimal('0'),
        verbose_name='Комиссия на вывод'
    )
    btc_profit = models.DecimalField(
        max_digits=25,
        decimal_places=8,
        default=Decimal('0'),
        verbose_name='Профит'
    )

    # LTC.
    ltc_deposit_available = models.BooleanField(default=True, verbose_name='Депозит доступен')
    ltc_withdrawal_available = models.BooleanField(default=True, verbose_name='Вывод доступен')
    ltc_withdrawal_commission = models.DecimalField(
        max_digits=25,
        decimal_places=8,
        default=Decimal('0'),
        verbose_name='Комиссия на вывод'
    )
    ltc_profit = models.DecimalField(
        max_digits=25,
        decimal_places=8,
        default=Decimal('0'),
        verbose_name='Профит'
    )

    # XMR.
    xmr_deposit_available = models.BooleanField(default=True, verbose_name='Депозит доступен')
    xmr_withdrawal_available = models.BooleanField(default=True, verbose_name='Вывод доступен')
    xmr_withdrawal_commission = models.DecimalField(
        max_digits=25,
        decimal_places=8,
        default=Decimal('0'),
        verbose_name='Комиссия на вывод'
    )
    xmr_profit = models.DecimalField(
        max_digits=25,
        decimal_places=8,
        default=Decimal('0'),
        verbose_name='Профит'
    )

    # USDT.
    usdt_deposit_available = models.BooleanField(default=True, verbose_name='Депозит доступен')
    usdt_withdrawal_available = models.BooleanField(default=True, verbose_name='Вывод доступен')
    usdt_withdrawal_commission = models.DecimalField(
        max_digits=25,
        decimal_places=8,
        default=Decimal('0'),
        verbose_name='Комиссия на вывод'
    )
    usdt_profit = models.DecimalField(
        max_digits=25,
        decimal_places=8,
        default=Decimal('0'),
        verbose_name='Профит'
    )

    class Meta:
        verbose_name = 'Настройки кошельков'
        verbose_name_plural = verbose_name

    def __str__(self):
        return ''

    def get_deposit_available(self, crypt):
        return getattr(self, f'{crypt.lower()}_deposit_available')

    def get_withdrawal_available(self, crypt):
        return getattr(self, f'{crypt.lower()}_withdrawal_available')

    def get_withdrawal_commission(self, crypt):
        return getattr(self, f'{crypt.lower()}_withdrawal_commission')

    def update_profit(self, crypt, amount):
        kwargs = {}

        match crypt:
            case 'BTC':
                kwargs['btc_profit'] = models.F('btc_profit') + amount

            case 'LTC':
                kwargs['ltc_profit'] = models.F('ltc_profit') + amount

            case 'XMR':
                kwargs['xmr_profit'] = models.F('xmr_profit') + amount

            case 'USDT':
                kwargs['usdt_profit'] = models.F('usdt_profit') + amount

        WalletsSettings.objects.select_for_update().filter(pk=self.pk).update(**kwargs)

    # BTC.
    @property
    def display_btc_reserve(self):
        crypt = CryptSettings.objects.get(name='BTC')
        wallets = tg_models.Wallet.objects.filter(crypt=crypt)
        balances = wallets.aggregate(models.Sum('balance'))['balance__sum'] or Decimal('0')

        return display_decimal(balances + Decimal(self.btc_profit))

    display_btc_reserve.fget.short_description = 'Баланс системы'

    @property
    def display_btc_balance(self):
        return display_decimal(wallets['BTC'].get_balance(wallets=True))

    display_btc_balance.fget.short_description = 'Баланс провайдера'

    # LTC.
    @property
    def display_ltc_reserve(self):
        crypt = CryptSettings.objects.get(name='LTC')
        wallets = tg_models.Wallet.objects.filter(crypt=crypt)
        balances = wallets.aggregate(models.Sum('balance'))['balance__sum'] or Decimal('0')

        return display_decimal(balances + Decimal(self.ltc_profit))

    display_ltc_reserve.fget.short_description = 'Баланс системы'

    @property
    def display_ltc_balance(self):
        return display_decimal(wallets['LTC'].get_balance(wallets=True))

    display_ltc_balance.fget.short_description = 'Баланс провайдера'

    # XMR.
    @property
    def display_xmr_reserve(self):
        crypt = CryptSettings.objects.get(name='XMR')
        wallets = tg_models.Wallet.objects.filter(crypt=crypt)
        balances = wallets.aggregate(models.Sum('balance'))['balance__sum'] or Decimal('0')

        return display_decimal(balances + Decimal(self.xmr_profit))

    display_xmr_reserve.fget.short_description = 'Баланс системы'

    @property
    def display_xmr_balance(self):
        return display_decimal(wallets['XMR'].get_balance(wallets=True))

    display_xmr_balance.fget.short_description = 'Баланс провайдера'

    # USDT.
    @property
    def display_usdt_reserve(self):
        crypt = CryptSettings.objects.get(name='USDT')
        wallets = tg_models.Wallet.objects.filter(crypt=crypt)
        balances = wallets.aggregate(models.Sum('balance'))['balance__sum'] or Decimal('0')

        return display_decimal(balances + Decimal(self.usdt_profit))

    display_usdt_reserve.fget.short_description = 'Баланс системы'

    @property
    def display_usdt_balance(self):
        return display_decimal(wallets['USDT'].get_balance(wallets=True))

    display_usdt_balance.fget.short_description = 'Баланс провайдера'