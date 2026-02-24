from django.contrib import admin
from general_settings.admin import CardAdmin

from django.utils.html import format_html

from .models import CardProxy, Trader, Order, WorkingShift

# Register your models here.


@admin.register(CardProxy)
class CardProxyAdmin(CardAdmin):
    pass


@admin.register(Trader)
class TraderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['client']
    list_display = ['name', 'client', 'balance', 'received', 'active', 'in_work']
    list_filter = ['active', 'in_work']
    search_fields = ['name', 'client__tg_id']

    @admin.display(description='Реквизиты')
    def requisites(self, obj):
        url = f'/admin/trading/cardproxy/?trader__id__exact={obj.id}'
        return format_html(f'<a href="{url}">Смотреть</a>')

    @admin.display(description='Заявки')
    def orders(self, obj):
        url = f'/admin/trading/order/?trader__id__exact={obj.id}'
        return format_html(f'<a href="{url}">Смотреть</a>')

    def add_view(self, request, extra_context=None):
        self.readonly_fields = []
        self.fieldsets = (
            (None, {'fields': ('name', 'client')}),
        )
        return super().add_view(request, extra_context=extra_context)

    def change_view(self, request, object_id, extra_context=None):
        self.readonly_fields = ['name', 'client', 'date_joined', 'in_work', 'requisites', 'orders']
        self.fieldsets = (
            (None, {'fields': ('name', 'client', 'date_joined', 'active')}),
            ('Трейдинг', {'fields': ('balance', 'received', 'in_work', 'requisites', 'orders')}),
        )

        return super().change_view(request, object_id, extra_context=extra_context)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'trader', '_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_id', 'amount', 'changed_amount', 'requisites']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description='Сумма')
    def _amount(self, obj):
        if obj.changed_amount is None:
            return format_html(f'<span class="nowrap">{obj.amount} RUB</span>')

        return format_html(f'<span class="nowrap"><s>{obj.amount} RUB</s> {obj.changed_amount} RUB</span>')

    fieldsets = (
        (None, {'fields': ('order_id', 'trader', 'status', 'created_at', 'changed_at')}),
        ('Платеж', {'fields': ('_amount', 'bank', 'cardholder_name', 'requisites')})
    )


@admin.register(WorkingShift)
class WorkingShiftAdmin(admin.ModelAdmin):
    list_display = ['id', 'trader', '_amount', 'created_at']
    list_filter = ['created_at']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description='Оборот')
    def _amount(self, obj):
        return format_html(f'<span class="nowrap">{obj.amount} RUB</span>')

    @admin.display(description='Заявки')
    def orders(self, obj):
        url = f'/admin/trading/order/?working_shift__id__exact={obj.id}'
        return format_html(f'<a href="{url}">Смотреть</a>')

    fieldsets = (
        (None, {'fields': ('id', 'trader', 'orders', '_amount', 'created_at')}),
    )





