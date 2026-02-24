from django.db import models, transaction
from django.utils.timezone import datetime
from datetime import timedelta
from django_ckeditor_5.fields import CKEditor5Field
from .modules_admin import messages
from general_settings.models import GeneralSettings, CryptSettings, Cashier, Card, CardStats, CryptSellSettings
from wallets import BTCWallet, LTCWallet, XMRWallet, USDTWallet, display_decimal
import time
import django_rq
import logging
import traceback
import random, string
import traceback
import  telebot
from decimal import Decimal, getcontext
from django_rq import get_queue, get_connection
from rq.job import Job
from rq.registry import ScheduledJobRegistry, StartedJobRegistry

# Create your models here.
static_path = 'telegram/static/img/'
wallets = {
    'BTC': BTCWallet.Wallet,
    'LTC': LTCWallet.Wallet,
    'XMR': XMRWallet.Wallet,
    'USDT': USDTWallet.Wallet,
}
logger = logging.getLogger('BOT')
sell_logger = logging.getLogger('SELL_CRYPT')

class RefLink(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Название')
    uuid = models.CharField(max_length=200, unique=True)

    class Meta:
        verbose_name = 'Реферальная ссылка'
        verbose_name_plural = 'Реферальные ссылки'

    def __str__(self):
        return self.name

    @property
    def link(self):
        return f'https://t.me/btcltcbot_bot?start={self.uuid}'

    def save(self, *args, **kwargs):
        if not self.pk:
            self.uuid = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for i in range(10))

        super().save(*args, **kwargs)


class Client(models.Model):
    ref_link = models.ForeignKey(
        RefLink,
        on_delete=models.SET_NULL,
        verbose_name='Реферальная ссылка',
        null=True,
        blank=True
    )

    father = models.BigIntegerField(null=True, blank=True, verbose_name='Пришел от')
    tg_id = models.BigIntegerField(unique=True, verbose_name='TG ID')
    username = models.CharField(max_length=200, null=True, blank=True, verbose_name='Имя пользователя')
    register_date = models.DateTimeField(verbose_name='Дата регистрации')

    count = models.PositiveIntegerField(default=0, verbose_name='Кол-во обменов')
    reject_count = models.PositiveIntegerField(default=0, verbose_name='Кол-во отклоненных заявок')

    ref_profit = models.IntegerField(default=0, verbose_name='Реферальный счет')
    ref_count = models.PositiveIntegerField(default=0, verbose_name='Кол-во рефералов')
    ref_percent = models.PositiveIntegerField(verbose_name='Процент по реф. программе', null=True)

    cashback = models.IntegerField(default=0, verbose_name='Кешбэк')
    discount = models.PositiveIntegerField(default=0, verbose_name='Скидка')
    spin_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Время последнего спина'
    )

    active_promocodes = models.TextField(null=True, verbose_name='Активные промокоды')
    old_promocodes = models.TextField(null=True, verbose_name='Использованные промокоды')

    state = models.CharField(max_length=50, null=True, blank=True)
    ban = models.BooleanField(default=False, verbose_name='Заблокирован')
    active = models.BooleanField(default=True, verbose_name='Активный')
    passed_captcha = models.BooleanField(default=False, verbose_name='Прошел капчу')
    scam = models.BooleanField(default=False, verbose_name='Скаммер')
    meta = models.JSONField('meta', default=dict)

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return str(self.tg_id)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @staticmethod
    def get_or_create(bot, message, start_value=None):
        tg_id = message.chat.id
        if tg_id < 0:
            return
            
        username = message.chat.username
        if not username:
            username = message.chat.first_name
        try:
            client = Client.objects.get(tg_id=tg_id)
            if username != client.username:
                client.username = username
                client.save()

            if not client.active:
                client.active = True
                client.save()
        except:
            client = Client.objects.create(
                tg_id=tg_id,
                username=username,
                register_date=datetime.now(),
            )

            if start_value and start_value.isdigit():
                qs = Client.objects.filter(tg_id=int(start_value))
                if qs.exists():
                    father = qs.first()
                    father.ref_count += 1
                    father.save()

                    client.father = father.tg_id
                    client.save()

            elif start_value:
                qs = RefLink.objects.filter(uuid=start_value)
                if qs.exists():
                    ref_link = qs.first()
                    client.ref_link = ref_link
                    client.save()

            client.update_meta()
        return client

    def update_meta(self):
        self.meta['order'] = {'promocode': None, 'discount': 0, 'bonus': False}
        self.meta['messages'] = {'trash_messages': []}
        self.save()

    def update_deposit_meta(self):
        if 'deposit_order' in self.meta.keys():
            del self.meta['deposit_order']
            self.save()

    def set_state(self, state):
        self.state = state
        self.save()

    def clear_state(self):
        self.state = None
        self.save()
    
    def update_sell_meta(self):
        self.meta['order_sell'] = {}
        self.save()

    def get_refferals(self):
        refferals = Client.objects.filter(father=self.tg_id)
        return refferals

    def get_old_promocodes(self):
        if self.old_promocodes and len(self.old_promocodes) > 0:
            promocodes = self.old_promocodes.split(';')
            return promocodes
        else:
            return []

    def get_active_promocodes(self):
        if self.active_promocodes and len(self.active_promocodes) > 0:
            promocodes = self.active_promocodes.split(';')
            return promocodes
        else:
            return []
        
    def get_ref_percent(self):
        if self.ref_percent:
            return self.ref_percent
        else:
            percent = 0
            if self.ref_count < 5:
                percent += 1
            elif self.ref_count > 5 and self.ref_count < 20:
                percent += 1.5
            else:
                percent += 2.5
            return percent

class Promocode(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Название')
    discount = models.PositiveIntegerField(verbose_name='Скидка')
    in_fiat = models.BooleanField(default=True, verbose_name='В рублях')
    one_off = models.BooleanField(default=False, verbose_name='Одноразовый')
    count = models.PositiveIntegerField(default=0, verbose_name='Кол-во использований')
    available = models.BooleanField(default=True, verbose_name='Активный')
    created_time = models.DateTimeField(default=datetime.now, verbose_name='Время создания')
    activated_time = models.DateTimeField(null=True, blank=True, verbose_name='Время активации')
    used_time = models.DateTimeField(null=True, blank=True, verbose_name='Время использования')
    used_treshold_value = models.PositiveIntegerField(verbose_name='Кол-во обменов для использования', blank=True, null=True, default=None)
    max_used_value = models.PositiveIntegerField(verbose_name='Максимальное кол-во использований', blank=True, null=True, default=None)
    expiration_date = models.DateTimeField(verbose_name="Дата окончания действия", blank=True, null=True, default=None)
    
    client_used = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name='Использовал',
        null=True,
        blank=True
    )


    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'промокоды'

    def __str__(self):
        return self.name

class Competition(models.Model):
    amount = models.PositiveIntegerField(
        default=500,
        verbose_name='Сумма выигрыша',
        help_text='В рублях'
    )
    from_amount = models.PositiveIntegerField(
        default=0,
        verbose_name='Учитывать обмены от',
        help_text='В рублях'
    )

    start_time = models.DateTimeField(auto_now_add=True, verbose_name='Дата начала')
    end_time = models.DateTimeField(verbose_name='Дата окончания', null=True, blank=True)

    winner = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name='Победитель',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Конкурс'
        verbose_name_plural = 'Конкурсы'

    def __str__(self):
        return f'Конкурс №{self.id}'

    @staticmethod
    def current():
        try:
            competition = Competition.objects.get(end_time=None)
        except:
            competition = None

        return competition

    def clients(self):
        orders = Order.objects.filter(competition=self)
        clients = [order.client for order in orders]
        return list(set(clients))

    def clients_url(self):
        url = '/admin/telegram/client/?q='
        query = '%2C'.join([str(client.tg_id) for client in self.clients()])
        return url + query

    def end(self):
        settings = GeneralSettings.objects.first()
        winner = random.choice(self.clients())
        self.winner = winner
        self.end_time = datetime.now()
        self.save()

        from telegram.handler import bot
        template = bot.get_template(messages.winner_message)
        mess = template.render(settings=settings)
        bot.send_message(winner, mess)

        if settings.chat_tg_id:
            template = bot.get_template(messages.end_competition_message)
            mess = template.render(settings=settings, amount=self.amount)
            bot.send_to_chat(mess)

    def save(self, *args, **kwargs):
        if not self.pk:
            settings = GeneralSettings.objects.first()
            if settings.chat_tg_id:
                from telegram.handler import bot
                template = bot.get_template(messages.start_competition_message)
                mess = template.render(competition=self)
                static_path = 'telegram/static/img/'
                bot.send_to_chat(mess, image=open(static_path+'competition.jpeg', 'rb'))
        super(Competition, self).save(*args, **kwargs)

class Notification(models.Model):
    bank = models.CharField(max_length=200)
    notification_type = models.CharField(max_length=200)
    pay = models.FloatField()
    balance = models.FloatField()
    datetime = models.DateTimeField()
    confirmed = models.BooleanField(default=False)
    used = models.BooleanField(default=False)
    label = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.id)

class Operator(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='Имя оператора')
    channel_tg_id = models.BigIntegerField(null=True, blank=True, verbose_name='TG ID кассы')
    balance = models.BigIntegerField(default=0, verbose_name='Баланс')

    class Meta:
        verbose_name = 'Оператор'
        verbose_name_plural = 'Операторы'

    def __str__(self):
        return self.name

class WorkingShift(models.Model):
    operator = models.ForeignKey(
        Operator,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Оператор'
    )
    
    start_time = models.DateTimeField(verbose_name='Дата начала')
    end_time = models.DateTimeField(verbose_name='Дата окончания', null=True, blank=True)
    night = models.BooleanField(default=False, verbose_name='Ночь')

    btc_course_start = models.FloatField(default=0, verbose_name='Курс BTC в начале смены')
    ltc_course_start = models.FloatField(default=0, verbose_name='Курс LTC в начале смены')
    xmr_course_start = models.FloatField(default=0, verbose_name='Курс XMR в начале смены')
    usdt_course_start = models.FloatField(default=90.65, verbose_name='Курс USDT в начале смены')

    btc_course_end = models.FloatField(default=0, verbose_name='Курс BTC в конце смены')
    ltc_course_end = models.FloatField(default=0, verbose_name='Курс LTC в конце смены')
    xmr_course_end = models.FloatField(default=0, verbose_name='Курс XMR в конце смены')
    usdt_course_end = models.FloatField(default=90.65, verbose_name='Курс USDT в конце смены')

    class Meta:
        verbose_name = 'Смена'
        verbose_name_plural = 'Смены'

    def __str__(self):
        return f'Смена №{self.id}'

    @staticmethod
    def current():
        working_shift = WorkingShift.objects.filter(end_time=None).first()
        if not working_shift:
            btc_wallet = wallets['BTC']
            ltc_wallet = wallets['LTC']
            xmr_wallet = wallets['XMR']
            usdt_wallet = wallets['USDT']
            working_shift = WorkingShift.objects.create(
                start_time=datetime.now(),
                btc_course_start=btc_wallet.get_course(),
                ltc_course_start=ltc_wallet.get_course(),
                xmr_course_start=xmr_wallet.get_course(),
                usdt_course_start=usdt_wallet.get_course()
            )
            
        return working_shift
        # try:
        #   working_shift = WorkingShift.objects.get(end_time=None)
        # except:
            # btc_wallet = wallets['BTC']
            # ltc_wallet = wallets['LTC']
            # xmr_wallet = wallets['XMR']
            # usdt_wallet = wallets['USDT']
            # working_shift = WorkingShift.objects.create(
            #   start_time=datetime.now(),
            #   btc_course_start=btc_wallet.get_course(),
            #   ltc_course_start=ltc_wallet.get_course(),
            #   xmr_course_start=xmr_wallet.get_course(),
            #   usdt_course_start=usdt_wallet.get_course()
            # )

        # return working_shift

    @property
    def orders_count(self):
        orders = Order.objects.filter(working_shift=self, status='confirmed')
        return orders.count()

    @property
    def orders_turnover(self):
        orders = Order.objects.filter(working_shift=self, status='confirmed')
        return sum(order.pay_value for order in orders)

    @property
    def orders_profit(self):
        orders = Order.objects.filter(working_shift=self, status='confirmed')
        profit = 0
        for order in orders:
            # profit += order.pay_value - (order.rub_value+order.fee_rub)
            order_profit = order.pay_value - (order.rub_value+order.fee_rub)
            # if order.label:
            #   order_profit -= round(order.pay_value * 0.02)

            profit += order_profit
            
        return profit

    @property
    def transactions_count(self):
        transactions = Transaction.objects.filter(working_shift=self, use_in_cashier=True)
        bills = Bill.objects.filter(working_shift=self, bill_type='Отправка')
        return transactions.count() + bills.count()

    @property
    def transactions_turnover(self):
        transactions = Transaction.objects.filter(working_shift=self, use_in_cashier=True)
        bills = Bill.objects.filter(working_shift=self, bill_type='Отправка')
        turnover = sum(transaction.pay_value for transaction in transactions) + sum(bill.pay_value for bill in bills)
        return turnover

    @property
    def transactions_profit(self):
        transactions = Transaction.objects.filter(working_shift=self, use_in_cashier=True)
        bills = Bill.objects.filter(working_shift=self, bill_type='Отправка')
        profit = 0
        for transaction in transactions:
            profit += transaction.pay_value - (transaction.rub_value+transaction.fee_rub)

        for bill in bills:
            profit += bill.profit
        return profit

    @property
    def purchases_count(self):
        purchases = Purchase.objects.filter(working_shift=self, use_in_cashier=True)
        bills = Bill.objects.filter(working_shift=self, bill_type='Закупка')
        return purchases.count() + bills.count()

    @property
    def purchases_profit(self):
        purchases = Purchase.objects.filter(working_shift=self, use_in_cashier=True)
        bills = Bill.objects.filter(working_shift=self, bill_type='Закупка')
        profit = 0
        for purchase in purchases:
            profit += purchase.rub_value - purchase.pay_value

        for bill in bills:
            profit += bill.profit
        return profit

    @property
    def turnover(self):
        orders = Order.objects.filter(working_shift=self, status='confirmed')
        transactions = Transaction.objects.filter(working_shift=self, use_in_cashier=True)
        return sum(order.pay_value for order in orders) + sum(transaction.pay_value for transaction in transactions)

    @property
    def transactions_turnover(self):
        transactions = Transaction.objects.filter(working_shift=self, use_in_cashier=True)
        bills = Bill.objects.filter(working_shift=self, bill_type='Отправка')
        turnover = sum(transaction.pay_value for transaction in transactions) + sum(bill.pay_value for bill in bills)
        return turnover

    @property
    def oper_turnover_profit(self):
        return int(self.turnover * 0.002)

    @property
    def oper_profit(self):
        profit = 100 * self.transactions_count
        profit += self.oper_turnover_profit

        if self.night:
            return 6000 + profit

        return 5000 + profit

        # all_purchases = self.purchases_profit

        # all_turnover = self.turnover or 1
        # transactions_turnover = self.transactions_turnover or 1

        # transactions_turnover_percent = round(transactions_turnover / (all_turnover / 100))
        # transactions_purchases_profit = round((all_purchases / 100) * transactions_turnover_percent)
        # transactions_profit = self.transactions_profit + transactions_purchases_profit

        # cashier = Cashier.objects.first()
        # profit = round((transactions_profit/100) * cashier.oper_percent)

        # return profit

        # cashier = Cashier.objects.first()
        # profit = self.transactions_profit
        # percent = cashier.oper_percent
        # return round((profit/100)*percent, 2)

    @property
    def oper_purchase_profit(self):
        purchases = Purchase.objects.filter(working_shift=self, use_in_cashier=True)
        profit = 0

        for purchase in purchases:
            if round(purchase.rub_value) < round(purchase.pay_value):
                continue

            profit += 100

            # value = purchase.rub_value

            # if value <= 20000:
            #     profit += 200

            # else:
            #     if self.night:
            #         profit += round((value/100) * 2)
            #     else:
            #         profit += round((value/100) * 1.5)

        return profit

    @property
    def oper_salary(self):
        if self.operator is None:
            return 0

        ws = Withdrawal.objects.filter(working_shift=self, purpose='Зарплата', operator=self.operator)
        amount = sum(w.pay_value for w in ws)

        return round(amount)

    @property
    def oper_balance(self):
        if self.operator:
            return self.operator.balance

        return '-'

    @property
    def turnover(self):
        orders = Order.objects.filter(working_shift=self, status='confirmed')
        transactions = Transaction.objects.filter(working_shift=self, use_in_cashier=True)
        return sum(order.pay_value for order in orders) + sum(transaction.pay_value for transaction in transactions)

    @property
    def withdrawal_amount(self):
        ws = Withdrawal.objects.filter(working_shift=self)
        amount = sum(w.pay_value for w in ws)

        return round(amount)

    @property
    def duty_amount(self):
        debts = Duty.objects.filter(working_shift=self)
        amount = sum(duty.amount for duty in debts)

        return round(amount)

    @property
    def discount_info(self):
        orders = Order.objects.filter(working_shift=self, status='confirmed')
        info = {
            'promocode': 0,
            'bonus_discount': 0,
            'lucky': 0,
            'cashback': 0
        }

        for order in orders:
            if order.discount_info is None:
                continue

            info['promocode'] += order.discount_info['promocode']
            info['bonus_discount'] += order.discount_info['bonus_discount']
            info['lucky'] += order.discount_info['lucky']
            info['cashback'] += order.discount_info['cashback']

        return info

    def check_for_close(self):
        btc_wallet = wallets['BTC']
        incomig_txs, outcomig_txs = btc_wallet.get_history()
        for tr in incomig_txs:
            txid = tr['txid']
            if Purchase.objects.filter(txid=txid, crypt='BTC').exists():
                continue
            else:
                print(f'BTC - {txid}')
                return False

        ltc_wallet = wallets['LTC']
        incomig_txs, outcomig_txs = ltc_wallet.get_history()
        for tr in incomig_txs:
            txid = tr['txid']
            if Purchase.objects.filter(txid=txid, crypt='LTC').exists():
                continue
            else:
                print(f'LTC - {txid}')
                return False

        xmr_wallet = wallets['XMR']
        incomig_txs, outcomig_txs = xmr_wallet.get_history()
        for tr in incomig_txs:
            txid = tr['txid']
            if Purchase.objects.filter(txid=txid, crypt='XMR').exists():
                continue
            else:
                print(f'XMR - {txid}')
                return False

        usdt_wallet = wallets['USDT']
        incomig_txs, outcomig_txs = usdt_wallet.get_history()
        for tr in incomig_txs:
            txid = tr['txid']
            if Purchase.objects.filter(txid=txid, crypt='USDT').exists():
                continue
            else:
                print(f'USDT - {txid}')
                return False

        return True

    def close(self):
        btc_wallet = wallets['BTC']
        ltc_wallet = wallets['LTC']
        xmr_wallet = wallets['XMR']
        usdt_wallet = wallets['USDT']
        self.end_time = datetime.now()
        self.btc_course_end = btc_wallet.get_course()
        self.ltc_course_end = ltc_wallet.get_course()
        self.xmr_course_end = xmr_wallet.get_course()
        self.usdt_course_end = usdt_wallet.get_course()
        self.save()

        if self.operator:
            operator = self.operator
            operator.balance += (int(self.oper_profit) + int(self.oper_purchase_profit))
            operator.save()
            self.save()

        WorkingShift.current()

    def volatility(self, crypt):
        if self.end_time:
            btc_course_end = self.btc_course_end
            ltc_course_end = self.ltc_course_end
            xmr_course_end = self.xmr_course_end
            usdt_course_end = self.usdt_course_end
        else:
            btc_wallet = wallets['BTC']
            ltc_wallet = wallets['LTC']
            xmr_wallet = wallets['XMR']
            usdt_wallet = wallets['USDT']
            btc_course_end = btc_wallet.get_course()
            ltc_course_end = ltc_wallet.get_course()
            xmr_course_end = xmr_wallet.get_course()
            usdt_course_end = usdt_wallet.get_course()

        if crypt == 'BTC':
            difference = btc_course_end - self.btc_course_start
            percent = difference/(self.btc_course_start/100)
            op = '+' if percent >= 0 else '-'
            return f'{round(btc_course_end)} руб ({op}{round(abs(percent), 2)}%)'

        if crypt == 'LTC':
            difference = ltc_course_end - self.ltc_course_start
            percent = difference/(self.ltc_course_start/100)
            op = '+' if percent >= 0 else '-'
            return f'{round(ltc_course_end)} руб ({op}{round(abs(percent), 2)}%)'

        if crypt == 'XMR':
            difference = xmr_course_end - self.xmr_course_start
            percent = difference/(self.xmr_course_start/100)
            op = '+' if percent >= 0 else '-'
            return f'{round(xmr_course_end)} руб ({op}{round(abs(percent), 2)}%)'

        if crypt == 'USDT':
            difference = usdt_course_end - self.usdt_course_start
            percent = difference/(self.usdt_course_start/100)
            op = '+' if percent >= 0 else '-'
            return f'{round(usdt_course_end)} руб ({op}{round(abs(percent), 2)}%)'

    def report(self, bot):
        template = bot.get_template(messages.working_shift_info_message)
        mess = template.render(working_shift=self)
        bot.send_report(mess)

        if self.operator is not None:
            template = bot.get_template(messages.working_shift_oper_info_message)
            mess = template.render(working_shift=self)

            bot.send_oper_report(self.operator, mess)

        cashier = Cashier.objects.first()

        if cashier:
            profit = self.orders_profit + self.transactions_profit + self.purchases_profit
            cashier.profit_balance += profit
            cashier.save()

            template = bot.get_template(messages.profit_message)
            mess = template.render(working_shift=self, balance=cashier.profit_balance)
            bot.send_profit_report(mess)


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', '⚠️ Ожидает подтверждения'),
        ('confirmed', '✅ Подтверждена'),
        ('cancelled', '❌ Отклонена'),
        ('timeouted', '⌛️ Просрочена'),
        ('error', '🆘 Ошибка при отправке')
    )

    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, verbose_name='Конкурс', null=True, blank=True)
    working_shift = models.ForeignKey(WorkingShift, on_delete=models.CASCADE, verbose_name='Смена', null=True)

    order_id = models.CharField(max_length=200, unique=True, verbose_name='ID обмена')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')
    crypt = models.CharField(max_length=200, verbose_name='Валюта')
    crypt_value = models.FloatField(verbose_name='Сумма')
    course = models.FloatField(verbose_name='Курс')
    rub_value = models.FloatField(verbose_name='Сумма в рублях')
    pay_value = models.FloatField(verbose_name='Сумма к оплате')
    address = models.CharField(max_length=200, verbose_name='Адрес')
    payment_method = models.CharField(max_length=200, verbose_name='Метод оплаты')
    requisites = models.TextField(verbose_name='Реквизиты')
    datetime = models.DateTimeField(verbose_name='Время создания заявки')
    updated_datetime = models.DateTimeField(null=True, blank=True, verbose_name='Время изменения')
    discount = models.FloatField(default=0, verbose_name='Скидка')
    cashback = models.FloatField(default=0, verbose_name='Кешбэк')
    promocode = models.CharField(max_length=200, null=True, verbose_name='Промокод')
    status = models.CharField(
        max_length=200,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    ref_value = models.FloatField(default=0, verbose_name='Сумма реферальных начислений')
    error = models.CharField(max_length=200, null=True, blank=True, verbose_name='Ошибка')
    tx_link = models.CharField(max_length=400, null=True, verbose_name='Ссылка на обозреватель')
    bonus_order = models.BooleanField(default=False, verbose_name='Бонусная заявка')
    fee = models.FloatField(default=0)
    fee_rub = models.FloatField(default=0)

    notification = models.OneToOneField(Notification, on_delete=models.CASCADE, null=True)
    message_id = models.BigIntegerField(null=True, blank=True)
    auto_handler = models.BooleanField(default=False)
    provider = models.CharField(max_length=200, null=True, blank=True, verbose_name='Провайдер')
    label = models.CharField(max_length=255, null=True, blank=True)
    payload = models.JSONField('payload', default=dict)
    discount_info = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = 'Обмен'
        verbose_name_plural = 'Обмены'

    def __str__(self):
        return self.order_id

    def left_time(self):
        settings = GeneralSettings.objects.first()
        given_seconds = settings.time_for_order * 60

        passed_seconds = (datetime.now() - self.datetime).seconds
        left_seconds = given_seconds - passed_seconds
        if left_seconds <= 0:
            return 0

        minutes = left_seconds // 60
        return minutes

    def get_timer(self):
        settings = GeneralSettings.objects.first()
        given_seconds = settings.time_for_order * 60

        passed_seconds = (datetime.now() - self.datetime).seconds
        left_seconds = given_seconds - passed_seconds
        if left_seconds <= 0:
            return '0:00'

        minutes = left_seconds // 60
        seconds = left_seconds - minutes * 60
        if seconds < 10:
            seconds = f'0{seconds}'
        return f'{minutes}:{seconds}'
    
    def is_happy_time(self):
        now = datetime.now().time()
        general_settings = GeneralSettings.objects.first()
        
        start_happy_time = general_settings.start_happy_time
        end_happy_time = general_settings.end_happy_time
        
        if start_happy_time and end_happy_time:
            if start_happy_time < end_happy_time:
                return start_happy_time <= now <= end_happy_time
            else:
                return now >= start_happy_time or now <= end_happy_time
        
        return False

    def is_unhappy_time(self):
        now = datetime.now().time()
        general_settings = GeneralSettings.objects.first()
        
        start_unhappy_time = general_settings.start_unhappy_time
        end_unhappy_time = general_settings.end_unhappy_time
        
        if start_unhappy_time and end_unhappy_time:
            if start_unhappy_time < end_unhappy_time:
                return start_unhappy_time <= now <= end_unhappy_time
            else:
                return now >= start_unhappy_time or now <= end_unhappy_time
        
        return False

    def add_cashback(self):
        settings = GeneralSettings.objects.first()
        percent = settings.cashback_percent

        profit = self.pay_value - self.rub_value
        if profit < 0:
            return 0
        
        if self.is_unhappy_time():
            percent -= settings.decrease_cashback_value
        elif self.is_happy_time():
            percent += settings.increase_cashback_value
            
        cashback = round(profit * (percent/100))
        if cashback <= 0:
            cashback = 1

        self.client.cashback += cashback
        self.client.save()
        self.save()
        return cashback

    def add_ref_profit(self):
        if self.client.father:
            father = Client.objects.get(tg_id=self.client.father)

            percent = father.get_ref_percent()
            profit = self.pay_value - self.rub_value
            ref_profit = round(profit * (percent/100))

            if ref_profit <= 0:
                ref_profit = 1

            self.ref_value = ref_profit
            self.save()

            father.ref_profit += ref_profit
            father.save()

    @property
    def expired_at(self):
        settings = GeneralSettings.objects.first()
        _expired_at = self.datetime + timedelta(minutes=settings.time_for_order)

        return _expired_at.strftime('%H:%M')

    def search_notification(self):
        time_start = self.datetime - timedelta(minutes=30)
        time_end = self.datetime + timedelta(minutes=30)
        notifications = Notification.objects.filter(
            datetime__range=[time_start, time_end],
            notification_type='Пополнение',
            pay=self.pay_value,
            confirmed=True,
            label=self.label
        )

        for notification in notifications:
            if notification.used and Order.objects.filter(notification=notification).exists():
                continue

            self.notification = notification
            self.notification.used = True
            self.notification.save()
            self.save()

            if 'card_id' in self.payload.keys():
                card = Card.objects.get(id=self.payload['card_id'])
                stats = CardStats.objects.filter(card=card, stopped_at=None).last()
                if stats:
                    stats.turnover = round(stats.turnover + notification.pay)
                    stats.save()

            break

    def reject(self, bot, admin_bot, timeout=False):
        order = self

        if order.status != 'pending':
            print(f'Return because not pending')
            return

        order.status = 'timeouted' if timeout else 'cancelled'
        order.updated_datetime = datetime.now()
        order.client.reject_count += 1
        order.client.save()
        order.save()

        admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)
        template = admin_bot.get_template(messages.order_message)
        mess = template.render(order=order)
        
        try:
            admin_bot.edit_message_text(admin, order.message_id, mess, reply_markup=None)
        except Exception as e:
            logger.error(f'Error editing admin confirm order message: {e}')

        if order.promocode:
            promocodes = order.client.get_active_promocodes()
            promocodes.append(order.promocode)
            order.client.active_promocodes = ';'.join(promocodes)
            order.client.save()
            order.save()

        template = bot.get_template(messages.reject_order_message)
        mess = template.render(order=order)
        bot.send_message(order.client, mess)

    def confirm(self, bot, admin_bot):
        with transaction.atomic():
            order = Order.objects.select_for_update().get(pk=self.pk)

            if order.status != 'pending':
                print(f'Return because not pending')
                return

            order.status = 'confirmed'
            order.save()

            try:
                wallet = wallets[order.crypt]
                settings = GeneralSettings.objects.first()
                admin = Client.objects.get(tg_id=settings.admin_tg_id)
                crypt_settings = CryptSettings.objects.get(name=order.crypt)
                template = admin_bot.get_template(messages.order_message)

                if order.client.scam:
                    send_result = 'Это скаммер, крипта не ушла'

                else:
                    fee = wallet.get_estimate_fee() if crypt_settings.auto_fee else crypt_settings.fee
                    send_result = wallet.send_crypt(order.address, order.crypt_value, fee)

            except:
                send_result = 'Что-то пошло не так. Проверьте историю отправок'

            if type(send_result) != dict:
                order.status = 'error'
                order.error = send_result
                order.save()

            else:
                try:
                    if order.promocode:
                        old_promocodes = order.client.get_old_promocodes()
                        old_promocodes.append(order.promocode)
                        order.client.old_promocodes = ';'.join(old_promocodes)

                    if order.cashback > 0:
                        order.client.cashback -= order.cashback
                        if order.client.cashback < 0:
                            order.client.cashback = 0

                    order.fee = send_result['fee']
                    order.fee_rub = round(send_result['fee'] * wallet.get_course())
                    order.updated_datetime = datetime.now()
                    order.tx_link = send_result['tx_link']
                    order.client.count += 1
                    order.client.save()
                    order.save()

                    order.add_ref_profit()

                except:
                    pass

        try:
            mess = template.render(order=order)
            time.sleep(1)
            try:
                admin_bot.edit_message_text(admin, order.message_id, mess, reply_markup=None)
            except Exception as e:
                logger.error(f'Error editing admin confirm order message: {e}')

            if order.status == 'confirmed':
                template = bot.get_template(messages.confirm_order_message)
                mess = template.render(order=order, support=settings.support_contact)
                bot.send_message(order.client, mess)

                try:
                    queue = django_rq.get_queue('default', default_timeout=-1)
                    queue.enqueue(Order.wait_for_confirmation, order.order_id, send_result['txid'])
                except Exception as e:
                    logger.error(f'Error with wait_for_confirmation: {e}')

                try:
                    competition = Competition.current()
                    if competition and order.rub_value >= competition.from_amount:
                        order.competition = competition
                        order.save()
                except:
                    logger.error(f'Error with competition: {e}')

                # mess = messages.review_message
                # keyboard = telebot.types.InlineKeyboardMarkup()
                # keyboard.row(
                #     telebot.types.InlineKeyboardButton(text='Оставить отзыв', callback_data=f'get_review-{order.order_id}')
                # )
                # bot.send_message(order.client, mess, reply_markup=keyboard)

        except Exception as e:
            logger.error({'order id': order.order_id, 'error': traceback.format_exc()})

    @staticmethod
    def wait_for_confirmation(order_id, tx_id):
        from .handler import bot
        settings = GeneralSettings.objects.first()

        order = Order.objects.get(order_id=order_id)
        wallet = wallets[order.crypt]
        template = bot.get_template(messages.tx_confirmed_message)
        mess = template.render(order=order, settings=settings)

        transaction = wallet.get_transaction(tx_id)
        confirmations = transaction['confirmations']
        while confirmations < 1:
            time.sleep(10)
            transaction = wallet.get_transaction(tx_id)
            confirmations = transaction['confirmations']
        bot.send_message(order.client, mess)


class Review(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name='Клиент'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='Обмен'
    )
    text = models.TextField(verbose_name='Текст')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
    
    def __str__(self):
        return f'{self.client}/{self.order.order_id}'


class Transaction(models.Model):
    working_shift = models.ForeignKey(WorkingShift, on_delete=models.CASCADE, verbose_name='Смена', null=True)
    crypt = models.CharField(max_length=200, verbose_name='Валюта')
    crypt_value = models.FloatField(verbose_name='Сумма')
    rub_value = models.FloatField(verbose_name='Сумма в рублях')
    fee = models.FloatField(verbose_name='Комиссия сети')
    fee_rub = models.FloatField(verbose_name='Комиссия сети в рублях')
    address = models.CharField(max_length=200, verbose_name='Адрес')
    tx_link = models.CharField(max_length=200, verbose_name='Ссылка на обозреватель')
    pay_value = models.FloatField(default=0, verbose_name='Сумма к оплате')
    use_in_cashier = models.BooleanField(default=True, verbose_name='Учитывать в кассе')

    class Meta:
        verbose_name = 'Ручная отправка'
        verbose_name_plural = 'Ручные отправки'

    def __str__(self):
        return f'{self.crypt_value} {self.crypt}'

    def report(self, bot):
        template = bot.get_template(messages.transaction_cashier_message)
        mess = template.render(transaction=self)
        bot.send_report(mess)

class Purchase(models.Model):
    working_shift = models.ForeignKey(WorkingShift, on_delete=models.CASCADE, verbose_name='Смена', null=True)
    txid = models.CharField(max_length=200, verbose_name='TX ID')
    crypt = models.CharField(max_length=200, verbose_name='Валюта')
    crypt_value = models.FloatField(verbose_name='Сумма')
    rub_value = models.FloatField(verbose_name='Сумма в рублях')
    pay_value = models.FloatField(verbose_name='Стоимость', default=0)
    datetime = models.DateTimeField(verbose_name='Дата закупки')
    tx_link = models.CharField(max_length=200, verbose_name='Ссылка на обозреватель')
    use_in_cashier = models.BooleanField(default=True, verbose_name='Учитывать в кассе')

    class Meta:
        verbose_name = 'Закупка'
        verbose_name_plural = 'Закупки'

    def __str__(self):
        return f'{self.crypt_value} {self.crypt}'

    def get_percent(self):
        loss = self.pay_value - self.rub_value
        percent = loss/(self.pay_value/100)
        # if self.pay_value > self.rub_value:
        #   percent *= -1
        return round(percent, 1)

    def report(self, bot):
        template = bot.get_template(messages.purchase_cashier_message)
        mess = template.render(purchase=self)
        bot.send_report(mess)

class Bill(models.Model):
    BILL_TYPE_CHOICES = (
        ('Закупка', 'Закупка'),
        ('Отправка', 'Отправка')
    )

    working_shift = models.ForeignKey(WorkingShift, on_delete=models.CASCADE, verbose_name='Смена', null=True)
    bill_type = models.CharField(max_length=50, choices=BILL_TYPE_CHOICES, verbose_name='Тип')
    rub_value = models.IntegerField(verbose_name='Номинальная сумма')
    pay_value = models.IntegerField(verbose_name='Оплаченная сумма')

    class Meta:
        verbose_name = 'Чек'
        verbose_name_plural = 'Чеки'

    def __str__(self):
        return str(self.id)

    @property
    def profit(self):
        if self.bill_type == 'Отправка':
            return self.pay_value - self.rub_value

        else:
            return self.rub_value - self.pay_value

format_config = {
    '<p>': '',
    '</p>': '\n',
    '&nbsp;': '\n',
    '<br>': '\n',
    '<p style="margin-left:0.0px;">': '',
    '<p style="margin-left:0px;">': '',
    '<span style="background-color:rgb(255,255,255);color:rgb(77,81,86);">': '',
    '</span>': ''
}

class Message(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название рассылки', help_text='Для админов', unique=True)
    message = CKEditor5Field('Текст', config_name='default')
    image = models.FileField(null=True, blank=True, verbose_name='Изображение', help_text='Необязательно')
    count_of_users = models.CharField(default='', max_length=200, verbose_name='Отправлено')
    pin_message_check_box = models.BooleanField(default=False, verbose_name='Сделать закреп')

    promocode = models.ForeignKey(
        Promocode,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Промокод',
        help_text='Отправляет всем, кто активировал выбранный промокод'
    )
    ref_father = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name='Рефовод',
        help_text='Отправляет рассылку всем рефераллам выбранного клиента',
        null=True,
        blank=True,
    )

    start_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата запуска',
        help_text='Если не указано, то рассылка будет запущена сразу же'
    )

    @property
    def status(self):
        redis_conn = django_rq.get_connection('low')
        queue = django_rq.get_queue(name='low', default_timeout=-1)

        scheduled_job_registry = ScheduledJobRegistry(queue=queue, connection=redis_conn)
        started_job_registry = StartedJobRegistry(queue=queue, connection=redis_conn)

        job_ids = (set(scheduled_job_registry.get_job_ids()) | set(started_job_registry.get_job_ids()))
        jobs = [Job.fetch(job_id, connection=redis_conn) for job_id in job_ids]
        status = 'ready'

        for job in jobs:
            job_args = job.args

            if not job_args:
                continue

            message = job_args[0]

            if hasattr(message, 'id') and message.id == self.id:
                if job.id in scheduled_job_registry.get_job_ids():
                    status = 'scheduled'

                elif job.id in started_job_registry.get_job_ids():
                    status = 'progress'

        return status

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Рассылка'

    def __str__(self):
        return self.title

    def formatted_message(self):
        message = self.message
        for key in format_config:
            message = message.replace(key, format_config[key])
        return message

STATUS_CHOICES = (
    ('✅ Выполнена', '✅ Выполнена'),
    ('❌ Отклонена', '❌ Отклонена'),
    ('⌛️ В ожидании', '⌛️ В ожидании'),

)

class WithdrawalRequest(models.Model):
    requests_id = models.CharField(max_length=200, unique=True, verbose_name='Номер заявки')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')
    summ = models.IntegerField(verbose_name='Сумма')
    datetime = models.DateTimeField(verbose_name='Время создания заявки')
    status = models.CharField(max_length=200, verbose_name='Статус', default='⌛️ В ожидании', choices=STATUS_CHOICES)

    class Meta:
        verbose_name = 'Заявка на вывод реф. счета'
        verbose_name_plural = 'Заявки на вывод реф. счета'

    def __str__(self):
        return self.requests_id


class Withdrawal(models.Model):
    working_shift = models.ForeignKey(
        WorkingShift,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='withdrawals',
        verbose_name='Смена'
    )
    operator = models.ForeignKey(
        Operator,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='withdrawals',
        verbose_name='Оператор'
    )
    purpose = models.CharField(max_length=200, verbose_name='Цель вывода средств')
    date = models.DateTimeField(verbose_name='Дата создания заявки')
    pay_value = models.FloatField(default=0, verbose_name='Сумма вывода в RUB')

    class Meta:
        verbose_name = 'Вывод'
        verbose_name_plural = 'Выводы'

    def __str__(self):
        return 'Заявка на вывод сдерств'


class Duty(models.Model):
    working_shift = models.ForeignKey(
        WorkingShift,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='debts',
        verbose_name='Смена'
    )
    client_name = models.CharField(max_length=200, verbose_name='Клиент')
    amount = models.IntegerField(default=0, verbose_name='Сумма')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата')

    class Meta:
        verbose_name = 'Долг'
        verbose_name_plural = 'Долги'

    def __str__(self):
        return f'Долг {self.client_name}'


class OrderSell(models.Model):
    STATUS_CHOICES = (
        ('pending', '⚠️ Ожидание оплаты'),
        ('partially', '⚠️ Частично оплачена (❗️ не выплачивать фиат до подтверждения)'),
        ('paid', '💸️ Оплачена (❗️ не выплачивать фиат до подтверждения)'),
        ('network_error', '❗️⛔️ Ошибка сети'),
        ('confirmed', '✅ Подтверждена'),
        ('completed', '🚀 Выполнена'),
        ('timeouted', '⌛️ Просрочена'),
    )

    order_id = models.CharField(max_length=200, unique=True, verbose_name='ID обмена')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')
    crypt = models.CharField(max_length=200, verbose_name='Валюта')
    crypt_value = models.FloatField(verbose_name='Сумма в крипте')
    recalculated_crypt_value = models.FloatField(null=True, verbose_name='Пересчитанная сумма в крипте')
    course = models.FloatField(verbose_name='Курс')
    rub_value = models.FloatField(verbose_name='Сумма в рублях')
    recalculated_rub_value = models.FloatField(null=True, verbose_name='Пересчитанная сумма в рублях')
    pay_value_with_percent = models.FloatField(verbose_name='Итоговая сумма оплаты с процентом', default=0)
    recalculated_pay_value_with_percent = models.FloatField(null=True, verbose_name='Итоговая пересчитанная сумма оплаты с процентом')
    address = models.CharField(max_length=200, verbose_name='Адрес')
    payment_method = models.CharField(max_length=200, verbose_name='Метод оплаты')
    requisites = models.TextField(verbose_name='Реквизиты')
    datetime = models.DateTimeField(verbose_name='Время создания заявки')
    updated_datetime = models.DateTimeField(null=True, blank=True, verbose_name='Время изменения')
    diff_payed_value = models.DecimalField(default=0, verbose_name='Разница итоговой и оплаченной суммы', decimal_places=8,  max_digits=20)
    transaction_id = models.CharField(null=True, verbose_name='ID транзакции', max_length=200)
    message_id = models.BigIntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=200,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    payload = models.JSONField('payload', default=dict)

    class Meta:
        verbose_name = 'Продажа'
        verbose_name_plural = 'Продажи'

    def __str__(self):
        return self.order_id

    def get_ru_status(self):
        return dict(self.STATUS_CHOICES).get(self.status, "⛔ Не найдена")

    def set_status(self, status_value, admin_bot, amount=None):
        getcontext().prec = 8

        epsilon = Decimal('0.0')
        admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)
        status = self.get_ru_status()

        if status_value == 'partially':
            if Decimal(str(self.diff_payed_value)) < epsilon:
                status = '💸️ Переведено больше чем нужно (❗️ не выплачивать фиат до подтверждения)'
            else:
                status = '⚠️ Частично оплачена (❗️ не выплачивать фиат до подтверждения)'

            crypt_currency = str(self.crypt)
            wallet = wallets.get(crypt_currency)
            crypt_settings = CryptSellSettings.objects.get(name=crypt_currency)
            percent = crypt_settings.percent
            course = wallet.get_course()

            crypt_value = amount
            rub_value = round(float(crypt_value) * course)
            rub_value_with_percent = round(rub_value - (rub_value * (percent / 100)))

            self.recalculated_crypt_value = amount
            self.recalculated_rub_value = rub_value
            self.recalculated_pay_value_with_percent = float(rub_value_with_percent)
            self.save()

            template = admin_bot.get_template(messages.order_sell_recalculate_message)
            mess = template.render(order_sell=self, status=status)
        elif status_value != 'network_error':
            template = admin_bot.get_template(messages.order_sell_message)
            mess = template.render(order_sell=self, status=status)
        else:
            status = '❗️⛔️ Ошибка сети'
            template = admin_bot.get_template(messages.order_sell_message)
            mess = template.render(order_sell=self, status=status)

        m = admin_bot.send_message(admin, mess, reply_markup=None)

        self.status = status_value
        self.updated_datetime = datetime.now()
        self.message_id = m.message_id
        self.save()

        # self.create_purchase()

    def set_diff_value(self, diff_value):
        self.diff_payed_value = diff_value
        self.updated_datetime = datetime.now()
        self.save()

    def get_timer(self):
        settings = GeneralSettings.objects.first()
        given_seconds = settings.time_for_sell * 60

        passed_seconds = (datetime.now() - self.datetime).seconds
        left_seconds = given_seconds - passed_seconds
        if left_seconds <= 0:
            return '0:00'

        minutes = left_seconds // 60
        seconds = left_seconds - minutes * 60
        if seconds < 10:
            seconds = f'0{seconds}'
        return f'{minutes}:{seconds}'

    def reject(self, bot, timeout=False):
        self.status = 'timeouted' if timeout else 'cancelled'
        self.updated_datetime = datetime.now()
        self.client.reject_count += 1
        self.client.save()
        self.save()

        # admin = Client.objects.get(tg_id=GeneralSettings.objects.first().admin_tg_id)
        # template = admin_bot.get_template(messages.order_sell_message)
        # status = self.get_ru_status()
        # mess = template.render(order_sell=order, status=status)
        # admin_bot.edit_message_text(admin, order.message_id, mess, reply_markup=None)

        template = bot.get_template(messages.reject_sell_order_message)
        mess = template.render(order_sell=self)
        bot.send_message(self.client, mess)

    def confirm(self, bot, admin_bot):
        self.status = 'confirmed'
        self.save()

        settings = GeneralSettings.objects.first()
        admin = Client.objects.get(tg_id=settings.admin_tg_id)
        template = admin_bot.get_template(messages.order_sell_message)
        status = self.get_ru_status()

        mess = template.render(order_sell=self, status=status)
        time.sleep(1)
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton(text='Выполнить', callback_data=f'complete_order_sell-{self.id}'),
        )
        if self.message_id:
            m = admin_bot.edit_message_text(admin, self.message_id, mess, reply_markup=keyboard)

        else:
            m = admin_bot.send_message(admin, mess, reply_markup=keyboard)

        try:
            message_id = m.message_id
            admin_bot.send_message(admin, '✅ Подтверждена', reply_to_message_id=message_id)

        except Exception as e:
            sell_logger.error(
                {
                    'action': 'Send to channel',
                    'order': self.order_id,
                    'error': traceback.format_exc()
                }
            )

        template = bot.get_template(messages.confirm_sell_order_message)
        mess = template.render(order_sell=self, support=settings.support_contact)
        bot.send_message(self.client, mess)

    def recalculation(self, bot, admin_bot):
        self.status = 'confirmed'
        self.save()

        status = self.get_ru_status()
        settings = GeneralSettings.objects.first()
        admin = Client.objects.get(tg_id=settings.admin_tg_id)

        template = admin_bot.get_template(messages.order_sell_recalculate_message)
        mess = template.render(order_sell=self, status=status)
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton(text='Выполнить', callback_data=f'complete_order_sell_rec-{self.id}'),
        )
        m = admin_bot.edit_message_text(admin, self.message_id, mess, reply_markup=keyboard)

        try:
            message_id = m.message_id
            admin_bot.send_message(admin, '✅ Подтверждена', reply_to_message_id=message_id)

        except Exception as e:
            sell_logger.error(
                {
                    'action': 'Send to channel',
                    'order': self.order_id,
                    'error': traceback.format_exc()
                }
            )

        template = bot.get_template(messages.confirm_sell_order_message)
        mess = template.render(order_sell=self, support=settings.support_contact)
        bot.send_message(self.client, mess)

    def create_purchase(self):
        match self.crypt:
            case 'BTC':
                tx_link = f"https://blockchair.com/en/bitcoin/transaction/{self.transaction_id}"

            case 'LTC':
                tx_link = f"https://blockchair.com/en/litecoin/transaction/{self.transaction_id}"

            # case 'XMR':
            #     tx_link = f"https://blockchair.com/en/bitcoin/transaction/{link}"
            #
            # case 'USDT':
            #     tx_link = f"https://blockchair.com/en/bitcoin/transaction/{link}"

        if self.recalculated_crypt_value is not None:
            crypt_value = self.recalculated_crypt_value
            rub_value = self.recalculated_rub_value
            pay_value_with_percent = self.recalculated_pay_value_with_percent

        else:
            crypt_value = self.crypt_value
            rub_value = self.rub_value
            pay_value_with_percent = self.pay_value_with_percent

        purchase = Purchase.objects.create(
            working_shift=WorkingShift.current(),
            txid=self.transaction_id,
            crypt=self.crypt,
            crypt_value=crypt_value,
            rub_value=rub_value,
            pay_value=pay_value_with_percent,
            datetime=self.datetime,
            tx_link=tx_link
        )
        purchase.save()

        from telegram.handler import bot
        purchase.report(bot)


class Wallet(models.Model):
    crypt = models.ForeignKey(CryptSettings, on_delete=models.PROTECT, verbose_name='Валюта')
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='wallets',
        verbose_name='Клиент'
    )
    address = models.CharField(max_length=255, null=True, verbose_name='Адрес')
    balance = models.DecimalField(
        max_digits=25,
        decimal_places=8,
        default=Decimal('0'),
        verbose_name='Баланс'
    )

    class Meta:
        verbose_name = 'Кошелек'
        verbose_name_plural = 'Кошельки'

    def __str__(self):
        return f'{self.crypt.name} - {self.client.tg_id}'

    def update_balance(self, amount):
        Wallet.objects.filter(pk=self.pk).update(balance=models.F('balance') + amount)


class WalletTransaction(models.Model):
    CATEGORY_CHOICES = (
        ('withdrawal', 'Вывод'),
        ('deposit', 'Депозит'),
    )

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='Кошелек'
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='Категория')
    internal = models.BooleanField(default=False, verbose_name='Внутренняя')
    tx_id = models.CharField(max_length=255, verbose_name='ID транзакции')
    explorer_link = models.CharField(
        null=True,
        max_length=255,
        verbose_name='Ссылка на обозреватель'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    address = models.CharField(max_length=255, verbose_name='Адрес')
    amount = models.DecimalField(max_digits=25, decimal_places=8, verbose_name='Сумма')
    commission = models.DecimalField(max_digits=25, decimal_places=8, verbose_name='Комиссия')
    provider_commission = models.DecimalField(max_digits=25, decimal_places=8, verbose_name='Комиссия провайдера')

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    def __str__(self):
        return self.tx_id

    @property
    def full_commission(self):
        return self.commission + self.provider_commission

    @property
    def display_amount(self):
        amount = display_decimal(self.amount)

        if self.category == 'deposit':
            amount = '+' + amount

        return amount

    @property
    def display_full_commission(self):
        return display_decimal(self.full_commission)
