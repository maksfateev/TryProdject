# -*- coding: utf-8 -*-
from general_settings.models import *
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Установка настроек'

    def handle(self, *args, **options):
        if not GeneralSettings.objects.exists():
            GeneralSettings.objects.create(
                time_for_payment=5,
                time_for_order=15,
                min_value_first=1000,
                auto_handler=False,
                boss_contact='None',
                support_contact='None',
                reviews_contact='None',
                chat_contact='None',
                news_contact='None',
                admin_tg_id=1111,
                ref_percent=5,
                cashback_percent=5,
                min_ref_withdrawal=500,
                cashback_order_count=5
            )

        crypts = ['BTC', 'LTC', 'XMR', 'USDT']
        sell_crypt = ['BTC', 'LTC', 'XMR', 'USDT']
        
        for crypt in crypts:
            if not CryptSettings.objects.filter(name=crypt).exists():
                c = CryptSettings.objects.create(name=crypt, percent=10)

                CryptPercent.objects.create(crypt=c, from_value=0, to_value=5000, percent=10)
                CryptPercent.objects.create(crypt=c, from_value=5000, to_value=10000, percent=10)
                CryptPercent.objects.create(crypt=c, from_value=10000, to_value=30000, percent=10)
                CryptPercent.objects.create(crypt=c, from_value=30000, to_value=50000, percent=10)
                CryptPercent.objects.create(crypt=c, from_value=50000, to_value=None, percent=10)

        for crypt in sell_crypt:
            if not CryptSellSettings.objects.filter(name=crypt).exists():
                CryptSellSettings.objects.create(name=crypt, percent=5)

        if not PaymentMethod.objects.exists():
            PaymentMethod.objects.create(
                card_name='Номер карты',
                card_description='test',

                sbp_name='Номер телефона',
                sbp_description='test'
            )

        if not Cashier.objects.exists():
            Cashier.objects.create(channel=-11111, oper_percent=50)

        if not WalletsSettings.objects.exists():
            WalletsSettings.objects.create()



















