from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponseRedirect

from .models import *
# Register your models here.

class BaseStatsAdmin(admin.ModelAdmin):
	def has_add_permission(self, request, obj=None):
		return False

	def has_change_permission(self, request, obj=None):
		return False

	def has_delete_permission(self, request, obj=None):
		return False

	def _count_registers(self, obj):
		return format_html(str(obj.count_registers()))
	_count_registers.short_description = 'Кол-во регистраций'

	def _count_payed_orders(self, obj):
		return format_html(str(obj.count_payed_orders()))
	_count_payed_orders.short_description = 'Кол-во оплаченных заявок'

	def _count_issued_requisites(self, obj):
		return format_html(str(obj.count_issued_requisites()))
	_count_issued_requisites.short_description = 'Кол-во выданных реквизитов'

	def _orders_about_issued_requisites(self, obj):
		issued_requisites = obj.count_issued_requisites()
		if issued_requisites == 0:
			percent = 100
		else:
			orders = obj.count_payed_orders()
			percent = orders / (issued_requisites / 100)
		return format_html(f'{round(percent, 2)}%')
	_orders_about_issued_requisites.short_description = 'Соотношение заявок к резвизитам'

	def _count_issued_pay_values(self, obj):
		return format_html(str(obj.count_issued_pay_values()))
	_count_issued_pay_values.short_description = 'Кол-во выданных сумм для оплаты'

	def _orders_about_issued_pay_values(self, obj):
		pay_values = obj.count_issued_pay_values()
		if pay_values == 0:
			percent = 100
		else:
			orders = obj.count_payed_orders()
			percent = orders / (pay_values / 100)
		return format_html(f'{round(percent, 2)}%')
	_orders_about_issued_pay_values.short_description = 'Соотношение заявок к суммам для оплаты'

	def _count_canceled_orders(self, obj):
		return format_html(str(obj.count_canceled_orders()))
	_count_canceled_orders.short_description = 'Кол-во отмененных заявок'

	# 0 - 5000

	def _count_payed_orders_0_5000(self, obj):
		return format_html(str(obj.count_payed_orders(from_value=0, to_value=5000)))
	_count_payed_orders_0_5000.short_description = 'Кол-во оплаченных заявок'

	def _count_issued_requisites_0_5000(self, obj):
		return format_html(str(obj.count_issued_requisites(from_value=0, to_value=5000)))
	_count_issued_requisites_0_5000.short_description = 'Кол-во выданных реквизитов'

	def _orders_about_issued_requisites_0_5000(self, obj):
		issued_requisites = obj.count_issued_requisites(from_value=0, to_value=5000)
		if issued_requisites == 0:
			percent = 100
		else:
			orders = obj.count_payed_orders(from_value=0, to_value=5000)
			percent = orders / (issued_requisites / 100)
		return format_html(f'{round(percent, 2)}%')
	_orders_about_issued_requisites_0_5000.short_description = 'Соотношение заявок к резвизитам'

	def _count_issued_pay_values_0_5000(self, obj):
		return format_html(str(obj.count_issued_pay_values(from_value=0, to_value=5000)))
	_count_issued_pay_values_0_5000.short_description = 'Кол-во выданных сумм для оплаты'

	def _orders_about_issued_pay_values_0_5000(self, obj):
		pay_values = obj.count_issued_pay_values(from_value=0, to_value=5000)
		if pay_values == 0:
			percent = 100
		else:
			orders = obj.count_payed_orders(from_value=0, to_value=5000)
			percent = orders / (pay_values / 100)
		return format_html(f'{round(percent, 2)}%')
	_orders_about_issued_pay_values_0_5000.short_description = 'Соотношение заявок к суммам для оплаты'

	def _count_canceled_orders_0_5000(self, obj):
		return format_html(str(obj.count_canceled_orders(from_value=0, to_value=5000)))
	_count_canceled_orders_0_5000.short_description = 'Кол-во отмененных заявок'

	# 5000-10000
	
	def _count_payed_orders_5000_10000(self, obj):
		return format_html(str(obj.count_payed_orders(from_value=5000, to_value=10000)))
	_count_payed_orders_5000_10000.short_description = 'Кол-во оплаченных заявок'

	def _count_issued_requisites_5000_10000(self, obj):
		return format_html(str(obj.count_issued_requisites(from_value=5000, to_value=10000)))
	_count_issued_requisites_5000_10000.short_description = 'Кол-во выданных реквизитов'

	def _orders_about_issued_requisites_5000_10000(self, obj):
		issued_requisites = obj.count_issued_requisites(from_value=5000, to_value=10000)
		if issued_requisites == 0:
			percent = 100
		else:
			orders = obj.count_payed_orders(from_value=5000, to_value=10000)
			percent = orders / (issued_requisites / 100)
		return format_html(f'{round(percent, 2)}%')
	_orders_about_issued_requisites_5000_10000.short_description = 'Соотношение заявок к резвизитам'

	def _count_issued_pay_values_5000_10000(self, obj):
		return format_html(str(obj.count_issued_pay_values(from_value=5000, to_value=10000)))
	_count_issued_pay_values_5000_10000.short_description = 'Кол-во выданных сумм для оплаты'

	def _orders_about_issued_pay_values_5000_10000(self, obj):
		pay_values = obj.count_issued_pay_values(from_value=5000, to_value=10000)
		if pay_values == 0:
			percent = 100
		else:
			orders = obj.count_payed_orders(from_value=5000, to_value=10000)
			percent = orders / (pay_values / 100)
		return format_html(f'{round(percent, 2)}%')
	_orders_about_issued_pay_values_5000_10000.short_description = 'Соотношение заявок к суммам для оплаты'

	def _count_canceled_orders_5000_10000(self, obj):
		return format_html(str(obj.count_canceled_orders(from_value=5000, to_value=10000)))
	_count_canceled_orders_5000_10000.short_description = 'Кол-во отмененных заявок'

	# 10000-30000
	
	def _count_payed_orders_10000_30000(self, obj):
		return format_html(str(obj.count_payed_orders(from_value=10000, to_value=30000)))
	_count_payed_orders_10000_30000.short_description = 'Кол-во оплаченных заявок'

	def _count_issued_requisites_10000_30000(self, obj):
		return format_html(str(obj.count_issued_requisites(from_value=10000, to_value=30000)))
	_count_issued_requisites_10000_30000.short_description = 'Кол-во выданных реквизитов'

	def _orders_about_issued_requisites_10000_30000(self, obj):
		issued_requisites = obj.count_issued_requisites(from_value=10000, to_value=30000)
		if issued_requisites == 0:
			percent = 100
		else:
			orders = obj.count_payed_orders(from_value=10000, to_value=30000)
			percent = orders / (issued_requisites / 100)
		return format_html(f'{round(percent, 2)}%')
	_orders_about_issued_requisites_10000_30000.short_description = 'Соотношение заявок к резвизитам'

	def _count_issued_pay_values_10000_30000(self, obj):
		return format_html(str(obj.count_issued_pay_values(from_value=10000, to_value=30000)))
	_count_issued_pay_values_10000_30000.short_description = 'Кол-во выданных сумм для оплаты'

	def _orders_about_issued_pay_values_10000_30000(self, obj):
		pay_values = obj.count_issued_pay_values(from_value=10000, to_value=30000)
		if pay_values == 0:
			percent = 100
		else:
			orders = obj.count_payed_orders(from_value=10000, to_value=30000)
			percent = orders / (pay_values / 100)
		return format_html(f'{round(percent, 2)}%')
	_orders_about_issued_pay_values_10000_30000.short_description = 'Соотношение заявок к суммам для оплаты'

	def _count_canceled_orders_10000_30000(self, obj):
		return format_html(str(obj.count_canceled_orders(from_value=10000, to_value=30000)))
	_count_canceled_orders_10000_30000.short_description = 'Кол-во отмененных заявок'

	# 30000-50000
	
	def _count_payed_orders_30000_50000(self, obj):
		return format_html(str(obj.count_payed_orders(from_value=30000, to_value=50000)))
	_count_payed_orders_30000_50000.short_description = 'Кол-во оплаченных заявок'

	def _count_issued_requisites_30000_50000(self, obj):
		return format_html(str(obj.count_issued_requisites(from_value=30000, to_value=50000)))
	_count_issued_requisites_30000_50000.short_description = 'Кол-во выданных реквизитов'

	def _orders_about_issued_requisites_30000_50000(self, obj):
		issued_requisites = obj.count_issued_requisites(from_value=30000, to_value=50000)
		if issued_requisites == 0:
			percent = 100
		else:
			orders = obj.count_payed_orders(from_value=30000, to_value=50000)
			percent = orders / (issued_requisites / 100)
		return format_html(f'{round(percent, 2)}%')
	_orders_about_issued_requisites_30000_50000.short_description = 'Соотношение заявок к резвизитам'

	def _count_issued_pay_values_30000_50000(self, obj):
		return format_html(str(obj.count_issued_pay_values(from_value=30000, to_value=50000)))
	_count_issued_pay_values_30000_50000.short_description = 'Кол-во выданных сумм для оплаты'

	def _orders_about_issued_pay_values_30000_50000(self, obj):
		pay_values = obj.count_issued_pay_values(from_value=30000, to_value=50000)
		if pay_values == 0:
			percent = 100
		else:
			orders = obj.count_payed_orders(from_value=30000, to_value=50000)
			percent = orders / (pay_values / 100)
		return format_html(f'{round(percent, 2)}%')
	_orders_about_issued_pay_values_30000_50000.short_description = 'Соотношение заявок к суммам для оплаты'

	def _count_canceled_orders_30000_50000(self, obj):
		return format_html(str(obj.count_canceled_orders(from_value=30000, to_value=50000)))
	_count_canceled_orders_30000_50000.short_description = 'Кол-во отмененных заявок'

	# 50000+
	
	def _count_payed_orders_50000_(self, obj):
		return format_html(str(obj.count_payed_orders(from_value=50000)))
	_count_payed_orders_50000_.short_description = 'Кол-во оплаченных заявок'

	def _count_issued_requisites_50000_(self, obj):
		return format_html(str(obj.count_issued_requisites(from_value=50000)))
	_count_issued_requisites_50000_.short_description = 'Кол-во выданных реквизитов'

	def _orders_about_issued_requisites_50000_(self, obj):
		issued_requisites = obj.count_issued_requisites(from_value=50000)
		if issued_requisites == 0:
			percent = 100
		else:
			orders = obj.count_payed_orders(from_value=50000)
			percent = orders / (issued_requisites / 100)
		return format_html(f'{round(percent, 2)}%')
	_orders_about_issued_requisites_50000_.short_description = 'Соотношение заявок к резвизитам'

	def _count_issued_pay_values_50000_(self, obj):
		return format_html(str(obj.count_issued_pay_values(from_value=50000)))
	_count_issued_pay_values_50000_.short_description = 'Кол-во выданных сумм для оплаты'

	def _orders_about_issued_pay_values_50000_(self, obj):
		pay_values = obj.count_issued_pay_values(from_value=50000)
		if pay_values == 0:
			percent = 100
		else:
			orders = obj.count_payed_orders(from_value=50000)
			percent = orders / (pay_values / 100)
		return format_html(f'{round(percent, 2)}%')
	_orders_about_issued_pay_values_50000_.short_description = 'Соотношение заявок к суммам для оплаты'

	def _count_canceled_orders_50000_(self, obj):
		return format_html(str(obj.count_canceled_orders(from_value=50000)))
	_count_canceled_orders_50000_.short_description = 'Кол-во отмененных заявок'


	fieldsets = (
		('Общая статистика', {'fields': (
			'_count_registers',
			('_count_payed_orders', '_count_canceled_orders'),
			('_count_issued_requisites', '_orders_about_issued_requisites'),
			('_count_issued_pay_values', '_orders_about_issued_pay_values')
			)
		}),
		('0р - 5000р', {'fields': (
			('_count_payed_orders_0_5000', '_count_canceled_orders_0_5000'),
			('_count_issued_requisites_0_5000', '_orders_about_issued_requisites_0_5000'),
			('_count_issued_pay_values_0_5000', '_orders_about_issued_pay_values_0_5000')
			)
		}),
		('5000р - 10000р', {'fields': (
			('_count_payed_orders_5000_10000', '_count_canceled_orders_5000_10000'),
			('_count_issued_requisites_5000_10000', '_orders_about_issued_requisites_5000_10000'),
			('_count_issued_pay_values_5000_10000', '_orders_about_issued_pay_values_5000_10000')
			)
		}),
		('10000р - 30000р', {'fields': (
			('_count_payed_orders_10000_30000', '_count_canceled_orders_10000_30000'),
			('_count_issued_requisites_10000_30000', '_orders_about_issued_requisites_10000_30000'),
			('_count_issued_pay_values_10000_30000', '_orders_about_issued_pay_values_10000_30000')
			)
		}),
		('30000р - 50000р', {'fields': (
			('_count_payed_orders_30000_50000', '_count_canceled_orders_30000_50000'),
			('_count_issued_requisites_30000_50000', '_orders_about_issued_requisites_30000_50000'),
			('_count_issued_pay_values_30000_50000', '_orders_about_issued_pay_values_30000_50000')
			)
		}),
		('50000р +', {'fields': (
			('_count_payed_orders_50000_', '_count_canceled_orders_50000_'),
			('_count_issued_requisites_50000_', '_orders_about_issued_requisites_50000_'),
			('_count_issued_pay_values_50000_', '_orders_about_issued_pay_values_50000_')
			)
		}),
	)

	def changelist_view(self, request):
		if not self.model.objects.exists():
			self.model.objects.create()

		model_pk = self.model.objects.first().pk
		return HttpResponseRedirect(f'/admin/stats/{self.model.__name__.lower()}/{model_pk}/change/')


@admin.register(DayStats)
class DayStatsAdmin(BaseStatsAdmin):
	pass

@admin.register(WeekStats)
class WeekStatsAdmin(BaseStatsAdmin):
	pass

@admin.register(MonthStats)
class MonthStatsAdmin(BaseStatsAdmin):
	pass

@admin.register(YearStats)
class YearStatsAdmin(BaseStatsAdmin):
	pass
















