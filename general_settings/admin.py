from django.contrib import admin
from .models import GeneralSettings, CryptSettings, PaymentMethod, Cashier, CryptPercent, Card, CardStats, CryptSellSettings, WalletsSettings, RequisitesRequest
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from wallets import display_decimal
# Register your models here.

@admin.register(GeneralSettings)
class GeneralSettingsAdmin(admin.ModelAdmin):
    def changelist_view(self, request):
        return HttpResponseRedirect('/admin/general_settings/generalsettings/1/change/')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = (
        ('Обмены', {'fields': ('time_for_payment', 'time_for_order', 'time_for_sell', 'min_value_first', 'auto_handler')}),
        ('Настройка обменов', {'fields': ('start_happy_time', 'end_happy_time', 'decrease_commission_value', 'increase_cashback_value', 'start_unhappy_time', 'end_unhappy_time', 'increase_commission_value', 'decrease_cashback_value')}),
        ('Контакты', {'fields': ('boss_contact', 'support_contact', 'reviews_contact', 'chat_contact', 'news_contact')}),
        ('Настройки TG ID', {'fields': ('admin_tg_id', 'chat_tg_id', 'reviews_tg_id')}),
        ('Ссылки', {'fields': ('channel_news', 'chat_link')}),
        ('Бонусы', {'fields': ('first_discount', 'cashback_percent', 'ref_percent', 'min_ref_withdrawal', 'cashback_order_count', 'cashback_order_amount')})
    )

class CryptPercentInline(admin.TabularInline):
    model = CryptPercent
    extra = 0
    readonly_fields = ['from_value', 'to_value']
    fieldsets = (
        ('', {'fields': ('from_value', 'to_value', 'percent')}),
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(CryptSellSettings)
class CryptSellSettingsAdmin(admin.ModelAdmin):
    list_display = ['name', 'percent', 'available']
    readonly_fields = ['name']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = (
        (None, {'fields': ('name', 'percent', 'min_value_sell', 'available', )}),
    )

    # def add_view(self, request, extra_content=None):
    # 	self.readonly_fields = []
    # 	self.fieldsets = (
    # 		('', {'fields': ('name', 'min_value_sell', 'available')}),
    # 	)
    # 	return super(CryptSellSettingsAdmin, self).add_view(request)

    # def change_view(self, request, object_id, extra_content=None):
    # 	self.readonly_fields = ['name']
    # 	self.fieldsets = (
    # 		('', {'fields': ('name', 'min_value_sell', 'available')}),
    # 	)
    # 	return super(CryptSellSettingsAdmin, self).change_view(request, object_id)

@admin.register(CryptSettings)
class CryptSettingsAdmin(admin.ModelAdmin):
    list_display = ['name', 'available']
    inlines = [CryptPercentInline]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def add_view(self, request, extra_content=None):
        self.readonly_fields = []
        self.fieldsets = (
            ('', {'fields': ('name', 'min_value', 'threshold_value', 'fix_comission', 'available')}),
        )
        return super(CryptSettingsAdmin, self).add_view(request)

    def change_view(self, request, object_id, extra_content=None):
        self.readonly_fields = ['name']
        self.fieldsets = (
            ('', {'fields': ('name', 'min_value', 'threshold_value', 'fix_comission', 'available')}),
        )
        return super(CryptSettingsAdmin, self).change_view(request, object_id)

class CardStatsInline(admin.TabularInline):
    model = CardStats
    extra = 0
    readonly_fields = ['turnover', 'started_at', 'stopped_at']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = (
        ('', {'fields': ('turnover', 'started_at', 'stopped_at')}),
    )

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    # list_display = ['id', 'user', 'bank', 'cardholder_name', 'short_number', '_status']
    list_filter = ['status', 'bank']
    search_fields = ['cardholder_name', 'card_number', 'phone_number']

    def _status(self, obj):
        color = ''

        match obj.status:
            case 'worked_all':
                color = 'green'

            case 'worked_card':
                color = 'green'

            case 'worked_sbp':
                color = 'green'

            case 'ready':
                color = '#bdbd2b'

            case 'not_worked':
                color = 'red'

            case 'blocked':
                color = 'red'
                
            case 'deleted':
                color = 'red'

        return format_html(f'<span style="color: {color};">{obj.get_status_display()}</span>')

    _status.short_description = 'Статус'

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        return qs.filter(user=request.user)

    def formfield_for_dbfield(self, *args, **kwargs):
        formfield = super().formfield_for_dbfield(*args, **kwargs)

        formfield.widget.can_delete_related = False
        formfield.widget.can_change_related = False
        formfield.widget.can_add_related = False
        formfield.widget.can_view_related = False

        return formfield

    def get_list_display(self, request):
        if request.user.is_superuser and request.user.username == 'developer':
            return ['id', 'card_owner', 'bank', 'cardholder_name', 'short_number', '_status', 'count']

        elif request.user.is_superuser:
            return ['id', 'card_owner', 'bank', 'cardholder_name', 'short_number', '_status']

        return ['id', 'bank', 'cardholder_name', 'short_number', '_status']

    def add_view(self, request, extra_context=None):
        self.inlines = []
        self.readonly_fields = []
        self.fieldsets = (
            ('', {'fields': ('bank', 'cardholder_name', 'card_number', 'phone_number')}),
        )
        return super().add_view(request, extra_context=extra_context)

    def change_view(self, request, object_id, extra_context=None):
        self.inlines = [CardStatsInline]
        self.readonly_fields = ['bank', 'card_owner']
        if request.user.is_superuser:
            self.fieldsets = (
                ('', {'fields': ('card_owner', 'bank', 'status', 'cardholder_name', 'card_number', 'phone_number')}),
            )
        else:
            self.fieldsets = (
                ('', {'fields': ('bank', 'status', 'cardholder_name', 'card_number', 'phone_number')}),
            )
        return super().change_view(request, object_id, extra_context=extra_context)

    def save_model(self, request, obj, form=None, change=False):
        if obj.user is None:
            obj.user = request.user

        obj.save()

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    # change_form_template = 'admin/change_payment_method.html'

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request):
        return HttpResponseRedirect('/admin/general_settings/paymentmethod/1/change/')

    readonly_fields = ['macro_link', 'macro_link1', 'xpay_balance', 'secrett_balance', 'pspware_balance', 'alfateam_balance', 'onlypays_balance', 'bridgepay_balance', 'bridgepay_tj_balance', 'bitzone_balance', 'wellbit_balance', 'extasypay_balance', 'infinitypay_balance', 'vita_balance', 'collybus_balance']
    fieldsets = (
        ('Настройки карты', {'fields': ('card_name', 'card_provider', 'card_provider_first_reserve', 'card_provider_second_reserve', 'card_provider_third_reserve', 'card_provider_fourth_reserve', 'card_provider_fifth_reserve', 'card_provider_sixth_reserve', 'card_provider_seventh_reserve', 'card_provider_eighth_reserve', 'card_description', 'card_on')}),
        ('Настройки СБП', {'fields': ('sbp_name', 'sbp_provider', 'sbp_provider_first_reserve', 'sbp_provider_second_reserve', 'sbp_provider_third_reserve', 'sbp_provider_fourth_reserve', 'sbp_provider_fifth_reserve', 'sbp_provider_sixth_reserve', 'sbp_provider_seventh_reserve', 'sbp_provider_eighth_reserve', 'sbp_description', 'sbp_on')}),
        ('Настройки Альфа-Альфа метода оплаты', {'fields': ('alfa_monobank_name', 'alfa_monobank_provider', 'alfa_monobank_provider_first_reserve', 'alfa_monobank_provider_second_reserve', 'alfa_monobank_provider_third_reserve', 'alfa_monobank_provider_fourth_reserve', 'alfa_monobank_provider_fifth_reserve', 'alfa_monobank_provider_sixth_reserve', 'alfa_monobank_provider_seventh_reserve', 'alfa_monobank_description', 'alfa_monobank_on')}),
        ('Настройки Сбер-Сбер метода оплаты', {'fields': ('sber_monobank_name', 'sber_monobank_provider', 'sber_monobank_provider_first_reserve', 'sber_monobank_provider_second_reserve', 'sber_monobank_description', 'sber_monobank_on')}),
        ('Настройки Озон-Озон метода оплаты', {'fields': ('ozon_monobank_name', 'ozon_monobank_provider', 'ozon_monobank_provider_first_reserve', 'ozon_monobank_provider_second_reserve', 'ozon_monobank_provider_third_reserve', 'ozon_monobank_provider_fourth_reserve', 'ozon_monobank_provider_fifth_reserve', 'ozon_monobank_provider_sixth_reserve', 'ozon_monobank_description', 'ozon_monobank_on')}),
        # ('Настройки Доп. метода оплаты', {'fields': ('add_method_name', 'add_method_provider', 'add_method_provider_first_reserve', 'add_method_provider_second_reserve', 'add_method_provider_third_reserve', 'add_method_description', 'add_method_on')}),
        ('Дополнительная информация', {'fields': ('macro_link', 'macro_link1', 'onlypays_balance', 'secrett_balance', 'alfateam_balance', 'pspware_balance', 'bitzone_balance', 'wellbit_balance', 'extasypay_balance', 'infinitypay_balance', 'vita_balance', 'collybus_balance')})
    )

    # def add_view(self, request, extra_content=None):
    # 	self.readonly_fields = []
    # 	self.fieldsets = (
    # 		('', {'fields': ('name', 'card_number', 'sbp_number')}),
    # 	)
    # 	return super(PaymentMethodAdmin, self).add_view(request)

    # def change_view(self, request, object_id, extra_content=None):
    # 	self.readonly_fields = ['macro_link', 'macro_link1']
    # 	self.fieldsets = (
    # 		('Отображение в боте', {'fields': ('name', 'name_description', 'sbp_name', 'sbp_description')}),
    # 		('Реквизиты', {'fields': ('card_number', 'sbp_number')}),
    # 		('Макро', {'fields': ('balance', 'macro_link', 'macro_link1')})
    # 	)
    # 	# self.fieldsets = (
    # 	# 	('', {'fields': ('name', 'sbp_name', 'card_number', 'sbp_number', 'balance', 'macro_link', 'macro_link1')}),
    # 	# )
    # 	return super(PaymentMethodAdmin, self).change_view(request, object_id)


@admin.register(RequisitesRequest)
class RequisitesRequestAdmin(admin.ModelAdmin):
    list_display = ['provider', 'tg_id', 'amount', 'requisites', 'success', 'created_date']
    list_filter = ['provider', 'success', 'created_date']
    search_fields = ['requisites', 'amount', 'tg_id']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


    fieldsets = (
        (None, {'fields': ('provider', 'tg_id', 'amount', 'requisites', 'success', 'created_date')}),
    )


@admin.register(Cashier)
class CashierAdmin(admin.ModelAdmin):
    def changelist_view(self, request):
        return HttpResponseRedirect('/admin/general_settings/cashier/1/change/')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(WalletsSettings)
class WalletsSettingsAdmin(admin.ModelAdmin):
    readonly_fields = [
        'display_btc_reserve',
        'display_btc_balance',
        'display_ltc_reserve',
        'display_ltc_balance',
        'display_xmr_reserve',
        'display_xmr_balance',
        'display_usdt_reserve',
        'display_usdt_balance'
    ]

    def changelist_view(self, request):
        return HttpResponseRedirect('/admin/general_settings/walletssettings/1/change/')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_object(self, request, object_id, from_field):
        obj = super().get_object(request, object_id, from_field=from_field)

        obj.btc_withdrawal_commission = display_decimal(obj.btc_withdrawal_commission)
        obj.btc_profit = display_decimal(obj.btc_profit)

        obj.ltc_withdrawal_commission = display_decimal(obj.ltc_withdrawal_commission)
        obj.ltc_profit = display_decimal(obj.ltc_profit)

        obj.xmr_withdrawal_commission = display_decimal(obj.xmr_withdrawal_commission)
        obj.xmr_profit = display_decimal(obj.xmr_profit)

        obj.usdt_withdrawal_commission = display_decimal(obj.usdt_withdrawal_commission)
        obj.usdt_profit = display_decimal(obj.usdt_profit)

        return obj

    # def display_btc_reserve(self, obj):
    # 	return obj.display_btc_reserve

    # def display_btc_balance(self, obj):
    # 	return obj.display_btc_balance

    fieldsets = (
        (
            'BTC',
            {
                'fields': (
                    'btc_deposit_available',
                    'btc_withdrawal_available',
                    'btc_withdrawal_commission',
                    'btc_profit',
                    'display_btc_reserve',
                    'display_btc_balance'
                )
            }
        ),
        (
            'LTC',
            {
                'fields': (
                    'ltc_deposit_available',
                    'ltc_withdrawal_available',
                    'ltc_withdrawal_commission',
                    'ltc_profit',
                    'display_ltc_reserve',
                    'display_ltc_balance'
                )
            }
        ),
        (
            'XMR',
            {
                'fields': (
                    'xmr_deposit_available',
                    'xmr_withdrawal_available',
                    'xmr_withdrawal_commission',
                    'xmr_profit',
                    'display_xmr_reserve',
                    'display_xmr_balance'
                )
            }
        ),
        (
            'USDT',
            {
                'fields': (
                    'usdt_deposit_available',
                    'usdt_withdrawal_available',
                    'usdt_withdrawal_commission',
                    'usdt_profit',
                    'display_usdt_reserve',
                    'display_usdt_balance'
                )
            }
        ),
    )






















