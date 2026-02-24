from django.db import models
from django.db.models import Q
from telegram.models import Client, Order

from django.utils import timezone
from datetime import timedelta
# Create your models here.

class IssuedRequisites(models.Model):
	client = models.ForeignKey(Client, on_delete=models.CASCADE)
	pay_value = models.IntegerField()
	datetime = models.DateTimeField(auto_now_add=True)


class IssuedPayValue(models.Model):
	client = models.ForeignKey(Client, on_delete=models.CASCADE)
	pay_value = models.IntegerField()
	datetime = models.DateTimeField(auto_now_add=True)


class CanceledOrder(models.Model):
	client = models.ForeignKey(Client, on_delete=models.CASCADE)
	pay_value = models.IntegerField()
	datetime = models.DateTimeField(auto_now_add=True)


class BaseStats(models.Model):
	period = None # day, week, month, year.
	
	@classmethod
	def get_query(cls, field_name):
		today = timezone.now().date().today()

		match cls.period:
			case 'year':
				return {f'{field_name}__year': today.year}

			case 'month':
				return {f'{field_name}__year': today.year, f'{field_name}__month': today.month}

			case 'week':
				return {f'{field_name}__week': today.isocalendar()[1]}

			case 'day':
				return {
					f'{field_name}__year': today.year,
					f'{field_name}__month': today.month,
					f'{field_name}__day': today.day
				}

			case _:
				raise Error('Period is None')

	@classmethod
	def count_issued_requisites(cls, from_value=None, to_value=None):
		query = cls.get_query('datetime')
		if from_value:
			query['pay_value__gte'] = from_value

		if to_value:
			query['pay_value__lt'] = to_value

		issued_requisites = IssuedRequisites.objects.filter(**query)
		return issued_requisites.count()

	@classmethod
	def count_issued_pay_values(cls, from_value=None, to_value=None):
		query = cls.get_query('datetime')
		if from_value:
			query['pay_value__gte'] = from_value

		if to_value:
			query['pay_value__lt'] = to_value

		pay_values = IssuedPayValue.objects.filter(**query)
		return pay_values.count()

	@classmethod
	def count_payed_orders(cls, from_value=None, to_value=None):
		query = cls.get_query('datetime')
		if from_value:
			query['pay_value__gte'] = from_value

		if to_value:
			query['pay_value__lt'] = to_value
			
		orders = Order.objects.filter(~Q(notification=None), **query)
		return orders.count()

	@classmethod
	def count_registers(cls):
		clients = Client.objects.filter(**cls.get_query('register_date'))
		return clients.count()

	@classmethod
	def count_canceled_orders(cls, from_value=None, to_value=None):
		query = cls.get_query('datetime')
		if from_value:
			query['pay_value__gte'] = from_value

		if to_value:
			query['pay_value__lt'] = to_value

		canceled_orders = CanceledOrder.objects.filter(**query)
		return canceled_orders.count()

	class Meta:
		abstract = True

	def __str__(self):
		return ''


class DayStats(BaseStats):
	period = 'day'

	class Meta:
		verbose_name = 'Статистика за сутки'
		verbose_name_plural = '1. Сутки'

class WeekStats(BaseStats):
	period = 'week'

	class Meta:
		verbose_name = 'Статистика за неделю'
		verbose_name_plural = '2. Неделя'

class MonthStats(BaseStats):
	period = 'month'

	class Meta:
		verbose_name = 'Статистика за месяц'
		verbose_name_plural = '3. Месяц'

class YearStats(BaseStats):
	period = 'year'

	class Meta:
		verbose_name = 'Статистика за год'
		verbose_name_plural = '4. Год'























