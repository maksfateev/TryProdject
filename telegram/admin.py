import time

from django.contrib import admin
from django.utils.html import format_html
from .models import *
from general_settings.models import GeneralSettings
from threading import Thread
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db.models import Case, When, IntegerField, Count, Q, Value, F
from django.db.models.functions import ExtractHour, Coalesce
from telegram.handler import bot
import os
from dotenv import load_dotenv
import datetime
import django_rq
import logging
import string, random
import django_rq
from rq.command import send_stop_job_command
from wallets import display_decimal
load_dotenv()
# Register your models here.

logger = logging.getLogger('MAILING')
LOCAL = bool(int(os.environ['LOCAL']))
admin.site.site_header = 'TESTBOT ADMIN'


def get_clients_by_hours(time_period):
    time_period_field_map = {
        'night': (0, 6),
        'morning': (6, 12),
        'day': (12, 18),
        'evening': (18, 24)
    }

    orders = Order.objects.all()
    filtered_clients = {}
    for order in orders:
        if order.status == 'confirmed':
            client_id = order.client.tg_id
            if client_id not in filtered_clients:
                filtered_clients[client_id] = {
                    'count': 0,
                    'night': 0,
                    'day': 0,
                    'morning': 0,
                    'evening': 0
                }
            filtered_clients[client_id]['count'] += 1
            order_hour = order.datetime.hour

            for period, (start, end) in time_period_field_map.items():
                if start <= order_hour and order_hour < end:
                    filtered_clients[client_id][period] += 1
                    break
    
    response = []

    for key, filtered_client in filtered_clients.items():
        if ((filtered_client[time_period] / filtered_client['count']) * 100) >= 50:
            response.append(key)

    response = list(set(response))
    clients = Client.objects.filter(tg_id__in=response)
    return clients


def mailing(message, group):
    settings = GeneralSettings.objects.first()
    if group == 'test':
        clients_ids = [settings.admin_tg_id, 371537043]
        clients = Client.objects.filter(tg_id__in=clients_ids)

    if group == 'all':
        clients = Client.objects.filter(active=True)

    if group == '0':
        clients = Client.objects.filter(count=0, active=True)

    if group == '1':
        clients = Client.objects.filter(count=1, active=True)

    if group == '1+':
        clients = Client.objects.filter(count__gte=1, active=True)

    if group == 'pidors':
        clients_ids = []
        now = datetime.datetime.now()
        qs = Client.objects.filter(count__gte=5, active=True)
        for client in qs:
            orders = Order.objects.filter(client=client, status='confirmed')
            last_order = orders.last()
            if last_order and (now - last_order.datetime).days >= 20:
                clients_ids.append(client.id)

        clients = Client.objects.filter(id__in=clients_ids)

    if group == 'night':
        clients = get_clients_by_hours(group)

    if group == 'day':
        clients = get_clients_by_hours(group)

    if group == 'morning':
        clients = get_clients_by_hours(group)

    if group == 'evening':
        clients = get_clients_by_hours(group)

    count = 0
    count_iter = 0
    clients_count = clients.count()
    mess = message.formatted_message()
    file_id = None

    if message.ref_father and group != 'test':
        clients = clients.filter(father=message.ref_father.tg_id)

    message.count_of_users = f'0 из {clients_count}'
    message.save()

    for client in clients:
        count_iter += 1

        if count_iter % 10 == 0:
            message.count_of_users = f'{count_iter} из {clients_count}'
            message.save()

        if count == 10:
            time.sleep(2)
            count = 0

        if message.promocode and group != 'test':
            active_promocodes = client.get_active_promocodes()
            if message.promocode.name not in active_promocodes:
                continue

        try:
            if message.image:
                animation_extensions = ['gif']
                image_extensions = ['png', 'jpg', 'jpeg']
                video_extensions = ['mp4', 'mov']

                extension = message.image.name.split('.')[-1]
                
                if extension in animation_extensions + video_extensions:
                    if file_id is None:
                        with open(message.image.path, 'rb') as f:
                            message_obj = bot.send_animation(client.tg_id, f, caption=mess, parse_mode='HTML')
                            file_id = message_obj.animation.file_id
                    else:
                        print(file_id)
                        message_obj = bot.send_animation(client.tg_id, file_id, caption=mess, parse_mode='HTML')
                else:
                    if file_id is None:
                        message_obj = bot.send_photo(client, open(message.image.path, 'rb'), caption=mess)
                        file_id = message_obj.photo[-1].file_id
                    else:
                        message_obj = bot.send_photo(client, file_id, caption=mess)
            else:
                message_obj = bot.send_message(client, mess)
                
            if message.pin_message_check_box:
                bot.pin_chat_message(chat_id=client.tg_id, message_id=message_obj.message_id)
                
            count += 1
            logger.info(f'Отправил сообщение {client.tg_id}. Рассылка: {message.title}')
        except Exception as e:
            deactivate_errors = [
                'Forbidden: bot was blocked by the user',
                'Forbidden: user is deactivated',
                'Bad Request: chat not found'
            ]
            if hasattr(e, 'description') and e.description in deactivate_errors:
                client.active = False
                client.save()

                logger.warning(f'{client.tg_id} - деактивирован')
            else:
                logger.error(f'{client.tg_id} - {e}')

            print(e)

@admin.register(RefLink)
class RefLinkAdmin(admin.ModelAdmin):
    list_display = ['name', '_link', '_refs_count']

    def _link(self, obj):
        return format_html(obj.link)
    _link.short_description = 'Ссылка'

    def _refs(self, obj):
        refs = Client.objects.filter(ref_link=obj)
        url = f'/admin/telegram/client/?ref_link__id__exact={obj.id}'
        return format_html(f'{refs.count()} - <a href="{url}">Смотреть</a>')
    _refs.short_description = 'Рефералы'

    def _refs_count(self, obj):
        refs = Client.objects.filter(ref_link=obj)
        return format_html(str(refs.count()))
    _refs_count.short_description = 'Кол-во рефералов'

    def _orders_count(self, obj):
        refs = Client.objects.filter(ref_link=obj)
        orders_count = sum([ref.count for ref in refs])
        return format_html(str(orders_count))
    _orders_count.short_description = 'Общее кол-во обменов'

    def _ordered_refs(self, obj):
        refs = Client.objects.filter(ref_link=obj, count__gte=1)
        return format_html(str(refs.count()))
    _ordered_refs.short_description = 'Кол-во рефералов с обменами'

    def add_view(self, request, extra_context=None):
        self.fieldsets = (
            ('', {'fields': ('name', )}),
        )
        self.readonly_fields = ['_link', '_refs', '_refs_count', '_orders_count', '_ordered_refs']
        return super().add_view(request, extra_context=extra_context)

    def change_view(self, request, object_id, extra_context=None):
        self.fieldsets = (
            ('', {'fields': ('name', '_link', '_refs', '_orders_count', '_ordered_refs')}),
        )
        self.readonly_fields = ['name', '_link', '_refs', '_refs_count', '_orders_count', '_ordered_refs']
        return super().change_view(request, object_id, extra_context=extra_context)


class ClientIsPidorFilter(admin.SimpleListFilter):
    title = 'Пидр'
    parameter_name = 'pidor'

    def lookups(self, request, model_admin):
        return [
            (True, 'Да')
        ]

    def queryset(self, request, queryset):
        if self.value():
            clients = []
            now = datetime.datetime.now()
            qs = queryset.filter(count__gte=5, active=True)
            for client in qs:
                orders = Order.objects.filter(client=client, status='confirmed')
                last_order = orders.last()
                if last_order and (now - last_order.datetime).days >= 20:
                    clients.append(client.id)

            return queryset.filter(id__in=clients)

        return queryset

class ClientCountFilter(admin.SimpleListFilter):
    title = 'Кол-во обменов'
    parameter_name = 'count'

    def lookups(self, request, model_admin):
        return [
            ('0', '0'),
            ('1', '1'),
            ('1+', '1+')
        ]

    def queryset(self, request, queryset):
        match self.value():
            case '0':
                queryset = queryset.filter(count=0)

            case '1':
                queryset = queryset.filter(count=1)

            case '1+':
                queryset = queryset.filter(count__gt=1)

        return queryset


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['tg_id', 'username', 'count', 'ref_count', 'register_date', 'passed_captcha']
    search_fields = ['tg_id', 'username']
    list_filter = ['passed_captcha', 'active', 'ban', ClientCountFilter, ClientIsPidorFilter, 'scam']
    readonly_fields = ['ref_link', 'tg_id', 'username', 'register_date', 'count', 'active_promocodes', 'old_promocodes', 'orders', '_father', 'referals', '_ref_profit', 'rejected_orders', 'discount', 'spin_time', '_discount', 'referals_count', '_cashback']

    def get_search_results(self, request, queryset, search_term):
            queryset, use_distinct = super().get_search_results(request, queryset, search_term)

            if search_term != '':
                try:
                    search_term = map(int, search_term.split(','))
                    queryset |= self.model.objects.filter(tg_id__in=search_term)

                except ValueError:
                    pass

            return queryset.distinct(), use_distinct

    def orders(self, obj):
        url = f'/admin/telegram/order/?client__id__exact={obj.id}&status=confirmed'
        return format_html(f"{obj.count} - <a href='{url}'>Смотреть</a>")
    orders.short_description = 'Обмены'

    def _discount(self, obj):
        return format_html(f'{obj.discount} RUB')
    _discount.short_description = 'Скидка'

    def rejected_orders(self, obj):
        url = f'/admin/telegram/order/?client__id__exact={obj.id}&status=cancelled'
        return format_html(f"{obj.reject_count} - <a href='{url}'>Смотреть</a>")
    rejected_orders.short_description = 'Отклоненные заявки'

    def _father(self, obj):
        if not obj.father:
            return format_html('-')
        father = Client.objects.get(tg_id=obj.father)
        url = f'/admin/telegram/client/{father.id}/change/'
        return format_html(f'<a href="{url}">{obj.father}</a>')
    _father.short_description = 'Пришел от'

    def referals(self, obj):
        url = f'/admin/telegram/client/?father={obj.tg_id}'
        return format_html(f'{obj.ref_count} - <a href="{url}">Смотреть</a>')
    referals.short_description = 'Кол-во рефералов'

    def referals_count(self, obj):
        referals = obj.get_refferals()
        return format_html(str(sum([referal.count for referal in referals])))
    referals_count.short_description = 'Кол-во обменов всех рефералов'

    def _ref_profit(self, obj):
        return format_html(f'{obj.ref_profit} RUB')
    _ref_profit.short_description = 'Реферальный счет'

    def _cashback(self, obj):
        return format_html(f'{obj.cashback} RUB')
    _cashback.short_description = 'Кешбэк'


    fieldsets = (
        (
            'Информация', {'fields': ('tg_id', 'username', 'register_date', '_father', 'ref_link')}
        ),
        (
            'Статистика', {'fields': ('orders', 'rejected_orders', '_cashback', 'ref_percent', 'referals', 'referals_count', 'ref_profit', 'active_promocodes', 'old_promocodes', '_discount', 'spin_time')}
        ),
        (
            'Действия', {'fields': ('ban', 'passed_captcha', 'scam')}
        ),
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'client_tg_id', 'crypt_value', 'crypt', '_discount', '_status', 'datetime']
    list_filter = ['crypt', 'status', 'provider']
    search_fields = ['order_id', 'address', 'pay_value', 'crypt_value', 'rub_value']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_search_results(self, request, queryset, search_term):
            queryset, use_distinct = super().get_search_results(request, queryset, search_term)
            if search_term != '':
                search_term = map(str, search_term.split(','))
                queryset |= self.model.objects.filter(order_id__in = search_term)
            return queryset.distinct(), use_distinct

    def _status(self, obj):
        return format_html(f'<span class="nowrap">{obj.get_status_display()}</span>')
    _status.short_description = 'Статус'

    def _datetime(self, obj):
        if obj.datetime:
            return format_html(f"{obj.datetime.strftime('%d-%m-%Y %H:%M:%S')}")
        else:
            return format_html(f"<p></p>")
    _datetime.short_description = 'Дата'

    def sended(self, obj):
        return format_html(f"{obj.crypt_value} {obj.crypt}")
    sended.short_description = 'Отправлено'

    def received(self, obj):
        return format_html(f"{obj.pay_value} руб")
    received.short_description = 'Получено'

    def client_tg_id(self, obj):
        url = f'/admin/telegram/client/{obj.client.id}/change/'
        return format_html(f"<a href='{url}'>{obj.client.tg_id}</a>", url=url)
    client_tg_id.short_description = 'Клиент'

    def client_username(self, obj):
        return format_html(f'{obj.client.username}')
    client_username.short_description = 'Имя пользователя'

    def client_count(self, obj):
        return format_html(f'{obj.client.count}')
    client_count.short_description = 'Кол-во обменов'

    def _sended(self, obj):
        return format_html(f"{'{:.8f}'.format(obj.crypt_value).rstrip('0').rstrip('.')} {obj.crypt} ({obj.rub_value} руб) на {obj.address}")
    _sended.short_description = 'К отправке'

    def _fee(self, obj):
        return format_html(f'{"{:.8f}".format(obj.fee).rstrip("0")} {obj.crypt} ~ {obj.fee_rub} руб')
    _fee.short_description = 'Комиссия сети'

    def _received(self, obj):
        return format_html(f"{obj.pay_value} руб")
    _received.short_description = 'Сумма к оплате'

    def _tx_link(self, obj):
        if not obj.tx_link:
            return format_html('-')
        url = obj.tx_link
        return format_html(f'<a href="{url}" target="blank">{url}</a>', url=url)
    _tx_link.short_description = 'Ссылка на транзакцию'

    def _discount(self, obj):
        return format_html(f'<span class="nowrap">{int(obj.discount)} руб</span>')
    _discount.short_description = 'Скидка'

    def payment(self, obj):
        if obj.notification:
            return format_html('❇️ Найдена')
        else:
            return format_html('⛔️ Не найдена')
    payment.short_description = 'Оплата'

    def _discount_info(self, obj):
        if obj.discount_info is None:
            return self._discount(obj)

        ul = f'''
            <p style="margin-bottom: 5px;"><b>{int(obj.discount)} руб</b></p>
            <ul style="margin-left: 0; padding-left: 0;">
                <li>Промокод: {obj.discount_info["promocode"]} руб</li>
                <li>Бонусная заявка: {obj.discount_info["bonus_discount"]} руб</li>
                <li>Рулетка: {obj.discount_info["lucky"]} руб</li>
                <li>Кешбек: {obj.discount_info["cashback"]} руб</li>
            </ul>
        '''

        return format_html(ul)
    _discount_info.short_description = 'Скидка'

    fieldsets = (
        ('Клиент', {'fields': ('client_tg_id', 'client_username', 'client_count')}),
        ('Информация', {'fields': ('_sended', '_fee', '_received', '_tx_link', 'datetime', 'updated_datetime', 'status', 'payment')}),
        ('Доп. информация', {'fields': ('provider', 'payment_method', 'requisites', 'promocode', '_discount_info', 'ref_value', 'bonus_order')})
    )

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['link', 'working_shift', 'crypt_value', 'crypt', 'rub_value', 'use_in_cashier']
    list_filter = ['crypt', 'use_in_cashier']
    search_fields = ['crypt_value', 'rub_value', 'address']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def link(self, obj):
        url = f'/admin/telegram/transaction/{obj.id}/change/'
        return format_html(f'<a href="{url}">Смотреть</a>')
    link.short_description = 'Действие'

    def _sended(self, obj):
        return format_html(f"{obj.crypt_value} {obj.crypt} на {obj.address}")
    _sended.short_description = 'Отправлено'

    def get_readonly_fields(self, request, obj=None):
        if obj:
            self.readonly_fields = ['_sended', '_tx_link', '_fee', '_working_shift', 'link']
            if obj.working_shift.end_time:
                self.readonly_fields.append('pay_value')
        return self.readonly_fields

    def _tx_link(self, obj):
        url = obj.tx_link
        if not url:
            return format_html('-')
        return format_html(f'<a href="{url}" target="blank">{url}</a>', url=url)
    _tx_link.short_description = 'Ссылка на транзакцию'

    def _fee(self, obj):
        return format_html(f"{'{:.8f}'.format(obj.fee)} {obj.crypt} ({obj.fee_rub} руб)")
    _fee.short_description = 'Комиссия сети'

    def _pay_value(self, obj):
        return format_html(f'{obj.pay_value} RUB')
    _pay_value.short_description = 'Сумма к оплате'

    def _working_shift(self, obj):
        url = f'/admin/telegram/workingshift/{obj.working_shift.id}/change/'
        return format_html(f'<a href="{url}">{obj.working_shift}</a>')
    _working_shift.short_description = 'Смена'

    fieldsets = (
        ('Информация', {'fields': ('_sended', '_fee', '_tx_link')}),
        ('Касса', {'fields': ('_working_shift', 'pay_value', 'use_in_cashier')})
    )

@admin.register(Promocode)
class PromocodeAdmin(admin.ModelAdmin):
    list_display = ['name', 'discount', 'in_fiat', 'count', 'one_off', 'available', 'created_time']
    list_filter = ['in_fiat', 'available', 'one_off']
    search_fields = ['name']

    def has_delete_permission(self, request, obj=None):
        return False

    def get_changeform_initial_data(self, request):
        random_name = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(10))
        return {'name': random_name}

    def add_view(self, request, extra_content=None):
        self.readonly_fields = []
        self.fieldsets = (
            ('', {'fields': ('name', 'discount', 'in_fiat', 'one_off', 'used_treshold_value', 'max_used_value', 'expiration_date')}),
        )
        return super(PromocodeAdmin, self).add_view(request)

    def change_view(self, request, object_id, extra_content=None):
        obj = Promocode.objects.get(id=object_id)

        self.readonly_fields = [
            'name',
            'discount',
            'in_fiat',
            'one_off',
            'count',
            'client_used',
            'created_time',
            'activated_time',
            'used_time'
        ]

        fields = ['name', 'discount', 'in_fiat', 'one_off', 'created_time', 'available', 'used_treshold_value', 'max_used_value', 'expiration_date']

        if obj.one_off:
            fields.append('activated_time')
            fields.append('used_time')
            fields.append('client_used')

        else:
            fields.append('count')

        self.fieldsets = (
            ('', {'fields': tuple(fields)}),
        )
        return super(PromocodeAdmin, self).change_view(request, object_id)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['title', 'status_admin']
    change_form_template = 'telegram/message_admin.html'
    autocomplete_fields = ['promocode', 'ref_father']
    readonly_fields = ['status_admin']

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        status = getattr(obj, 'status', '')
        context.update({
            'show_save': False,
            'show_save_and_continue': True if status == 'ready' or status == '' else False,
            'show_save_and_add_another': False,
            'show_delete': True if status == 'ready' else False,
            'status': obj.status if obj else ''
        })
        return super().render_change_form(request, context, add, change, form_url, obj)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)

        if not (obj and obj.status == 'progress'):
            fields = [field for field in fields if field != 'count_of_users']

        return fields

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['status_admin']

        if obj and obj.status == 'progress':
            readonly_fields.append('count_of_users')

        return readonly_fields

    @admin.display(description='Статус')
    def status_admin(self, obj):
        statuses = {
            'ready': '✅ Готова к работе',
            'progress': '🛠️ В работе',
            'scheduled': '⌛️ Запланирована'
        }

        return statuses[obj.status]

    def response_change(self, request, obj):
        if obj.start_at is not None and obj.start_at < datetime.datetime.now():
            if '_stop-mailing' not in request.POST and '_close-mailing' not in request.POST:
                messages.add_message(request, messages.ERROR, 'Дата запуска не может быть меньше текущего времени')
                return HttpResponseRedirect(".")

        if "_start-mailing-test" in request.POST:
            if LOCAL:
                thread = Thread(target=mailing, args=(obj, 'test'))
                thread.start()
            else:
                queue = django_rq.get_queue('low', default_timeout=-1)

                if obj.start_at is not None:
                    queue.enqueue_at(obj.start_at, mailing, obj, 'test')
                else:
                    queue.enqueue(mailing, obj, 'test')

            messages.add_message(request, messages.INFO, 'Рассылка началась!')
            return HttpResponseRedirect(".")

        elif "_start-mailing-all" in request.POST:
            if LOCAL:
                thread = Thread(target=mailing, args=(obj, 'all'))
                thread.start()
            else:

                queue = django_rq.get_queue('low', default_timeout=-1)
                if obj.start_at is not None:
                    queue.enqueue_at(obj.start_at, mailing, obj, 'all')
                else:
                    queue.enqueue(mailing, obj, 'all')

            messages.add_message(request, messages.INFO, 'Рассылка началась!')
            return HttpResponseRedirect(".")

        elif "_start-mailing-0" in request.POST:
            if LOCAL:
                thread = Thread(target=mailing, args=(obj, '0'))
                thread.start()
            else:
                queue = django_rq.get_queue('low', default_timeout=-1)
                if obj.start_at is not None:
                    queue.enqueue_at(obj.start_at, mailing, obj, '0')
                else:
                    queue.enqueue(mailing, obj, '0')

            messages.add_message(request, messages.INFO, 'Рассылка началась!')
            return HttpResponseRedirect(".")

        elif "_start-mailing-1" in request.POST:
            if LOCAL:
                thread = Thread(target=mailing, args=(obj, '1'))
                thread.start()
            else:
                queue = django_rq.get_queue('low', default_timeout=-1)
                if obj.start_at is not None:
                    queue.enqueue_at(obj.start_at, mailing, obj, '1')
                else:
                    queue.enqueue(mailing, obj, '1')

            messages.add_message(request, messages.INFO, 'Рассылка началась!')
            return HttpResponseRedirect(".")

        elif "_start-mailing-1_plus" in request.POST:
            if LOCAL:
                thread = Thread(target=mailing, args=(obj, '1+'))
                thread.start()
            else:
                queue = django_rq.get_queue('low', default_timeout=-1)
                if obj.start_at is not None:
                    queue.enqueue_at(obj.start_at, mailing, obj, '1+')
                else:
                    queue.enqueue(mailing, obj, '1+')

            messages.add_message(request, messages.INFO, 'Рассылка началась!')
            return HttpResponseRedirect(".")

        elif "_start-mailing-pidors" in request.POST:
            if LOCAL:
                thread = Thread(target=mailing, args=(obj, 'pidors'))
                thread.start()
            else:
                queue = django_rq.get_queue('low', default_timeout=-1)
                if obj.start_at is not None:
                    queue.enqueue_at(obj.start_at, mailing, obj, 'pidors')
                else:
                    queue.enqueue(mailing, obj, 'pidors')

            messages.add_message(request, messages.INFO, 'Рассылка началась!')
            return HttpResponseRedirect(".")

        elif "_stop-mailing" in request.POST:
            if not LOCAL:
                redis_conn = django_rq.get_connection('low')
                queue = django_rq.get_queue(name='low', default_timeout=-1)
                started_job_registry = StartedJobRegistry(queue=queue, connection=redis_conn)
                job_ids = (set(started_job_registry.get_job_ids()))
                jobs = [Job.fetch(job_id, connection=redis_conn) for job_id in job_ids]
                for job in jobs:
                    job_args = job.args
                    if not job_args:
                        continue
                    message = job_args[0]

                    if hasattr(message, 'id') and message.id == obj.id:
                        send_stop_job_command(redis_conn, job._id)
                        job.delete()

            messages.add_message(request, messages.INFO, 'Рассылка остановлена!')
            return HttpResponseRedirect(".")

        elif "_close-mailing" in request.POST:
            if not LOCAL:
                redis_conn = django_rq.get_connection('low')
                queue = django_rq.get_queue(name='low', default_timeout=-1)
                scheduled_job_registry = ScheduledJobRegistry(queue=queue, connection=redis_conn)
                job_ids = (set(scheduled_job_registry.get_job_ids()))
                jobs = [Job.fetch(job_id, connection=redis_conn) for job_id in job_ids]
                for job in jobs:
                    job_args = job.args
                    if not job_args:
                        continue
                    message = job_args[0]
                    if hasattr(message, 'id') and message.id == obj.id:
                        job.delete()
            messages.add_message(request, messages.INFO, 'Рассылка отменена!')
            return HttpResponseRedirect(".")
        
        elif "_start-mailing-night" in request.POST:
            if LOCAL:
                thread = Thread(target=mailing, args=(obj, 'night'))
                thread.start()
            else:
                queue = django_rq.get_queue('low', default_timeout=-1)
                if obj.start_at is not None:
                    queue.enqueue_at(obj.start_at, mailing, obj, 'night')
                else:
                    queue.enqueue(mailing, obj, 'night')
            messages.add_message(request, messages.INFO, 'Рассылка началась!')
            return HttpResponseRedirect(".")
        
        elif "_start-mailing-morning" in request.POST:
            if LOCAL:
                thread = Thread(target=mailing, args=(obj, 'morning'))
                thread.start()
            else:
                queue = django_rq.get_queue('low', default_timeout=-1)
                if obj.start_at is not None:
                    queue.enqueue_at(obj.start_at, mailing, obj, 'morning')
                else:
                    queue.enqueue(mailing, obj, 'morning')
            messages.add_message(request, messages.INFO, 'Рассылка началась!')
            return HttpResponseRedirect(".")
        
        elif "_start-mailing-day" in request.POST:
            if LOCAL:
                thread = Thread(target=mailing, args=(obj, 'day'))
                thread.start()
            else:
                queue = django_rq.get_queue('low', default_timeout=-1)
                if obj.start_at is not None:
                    queue.enqueue_at(obj.start_at, mailing, obj, 'day')
                else:
                    queue.enqueue(mailing, obj, 'day')
            messages.add_message(request, messages.INFO, 'Рассылка началась!')
            return HttpResponseRedirect(".")
        
        elif "_start-mailing-evening" in request.POST:
            if LOCAL:
                thread = Thread(target=mailing, args=(obj, 'evening'))
                thread.start()
            else:
                queue = django_rq.get_queue('low', default_timeout=-1)
                if obj.start_at is not None:
                    queue.enqueue_at(obj.start_at, mailing, obj, 'evening')
                else:
                    queue.enqueue(mailing, obj, 'evening')
            messages.add_message(request, messages.INFO, 'Рассылка началась!')
            return HttpResponseRedirect(".")
        
        return super().response_change(request, obj)


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ['requests_id', 'client_tg_id', 'summ', 'status']
    list_filter = ['status']
    search_fields = ['requests_id', 'client', 'summ']
    readonly_fields = ['client_tg_id', 'requests_id', '_datetime', '_summ']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def _datetime(self, obj):
        if obj.datetime:
            return format_html(f"{obj.datetime.strftime('%d-%m-%Y %H:%M:%S')}")
        else:
            return format_html(f"<p></p>")
    _datetime.short_description = 'Дата'

    def _summ(self, obj):
        return format_html(f'{obj.summ} RUB')
    _summ.short_description = 'Сумма'

    def client_tg_id(self, obj):
        url = f'/admin/telegram/client/{obj.client.id}/change/'
        return format_html(f"<a href='{url}'>{obj.client.tg_id}</a>", url=url)
    client_tg_id.short_description = 'Клиент'

    fieldsets = (
        ('', {'fields': ('requests_id', 'client_tg_id', '_summ', '_datetime', 'status')}),
    )

# @admin.register(StartPromocode)
# class StartPromocodeAdmin(admin.ModelAdmin):
#   autocomplete_fields = ['promocode']

#   def has_add_permission(self, request, obj=None):
#       return False

#   def has_delete_permission(self, request, obj=None):
#       return False

#   def changelist_view(self, request):
#       return HttpResponseRedirect('/admin/telegram/startpromocode/1/change/')

@admin.register(Purchase)
class PurchaseAdmmin(admin.ModelAdmin):
    list_display = ['link', 'working_shift', 'crypt_value', 'crypt', 'datetime', 'use_in_cashier']
    list_filter = ['use_in_cashier', 'crypt']
    search_fields = ['txid', 'crypt_value', 'rub_value', 'pay_value']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def link(self, obj):
        url = f'/admin/telegram/purchase/{obj.id}/change/'
        return format_html(f'<a href="{url}">Смотреть</a>')
    link.short_description = 'Действие'

    def get_readonly_fields(self, request, obj=None):
        if obj:
            self.readonly_fields = ['txid', 'amount', 'datetime', '_tx_link', '_working_shift', 'link']
            if obj.working_shift.end_time:
                self.readonly_fields.append('pay_value')
        return self.readonly_fields

    def amount(self, obj):
        return format_html(f'{obj.crypt_value} {obj.crypt} ({obj.rub_value} RUB)')
    amount.short_description = 'Получено'

    def _tx_link(self, obj):
        url = obj.tx_link
        return format_html(f'<a href="{url}" target="blank">{url}</a>', url=url)
    _tx_link.short_description = 'Ссылка на транзакцию'

    def _working_shift(self, obj):
        url = f'/admin/telegram/workingshift/{obj.working_shift.id}/change/'
        return format_html(f'<a href="{url}">{obj.working_shift}</a>')
    _working_shift.short_description = 'Смена'

    fieldsets = (
        ('', {'fields': ('_working_shift', 'txid', 'amount', 'pay_value', 'datetime', '_tx_link', 'use_in_cashier')}),
    )


@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ['name', 'balance']


@admin.register(WorkingShift)
class WorkingShiftAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'night', 'full_profit', '_turnover']
    readonly_fields = ['name']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def name(self, obj):
        return format_html(f'{obj}')
    name.short_description = 'Номер'

    def orders(self, obj):
        url = f'/admin/telegram/order/?working_shift__id__exact={obj.id}'
        return format_html(f'{obj.orders_count} - <a href="{url}">Смотреть</a> <b style="padding-left: 10px">{obj.orders_profit} руб</b>')
    orders.short_description = 'Обмены'

    def transactions(self, obj):
        url = f'/admin/telegram/transaction/?working_shift__id__exact={obj.id}&use_in_cashier=True'
        return format_html(f'{obj.transactions_count} - <a href="{url}">Смотреть</a> <b style="padding-left: 10px">{obj.transactions_profit} руб</b>')
    transactions.short_description = 'Ручные отправки'

    def purchases(self, obj):
        url = f'/admin/telegram/purchase/?working_shift__id__exact={obj.id}&use_in_cashier=True'
        return format_html(f'{obj.purchases_count} - <a href="{url}">Смотреть</a> <b style="padding-left: 10px">{obj.purchases_profit} руб</b>')
    purchases.short_description = 'Закупки'

    def full_profit(self, obj):
        return format_html(f'<b>{obj.orders_profit+obj.transactions_profit+obj.purchases_profit} руб</b>')
    full_profit.short_description = 'Общий профит'

    def bot_profit(self, obj):
        return format_html(f'<b>{obj.orders_profit+obj.transactions_profit+obj.purchases_profit-obj.oper_profit} руб</b>')
    bot_profit.short_description = 'Профит обменника'

    def _oper_profit(self, obj):
        return format_html(f'<b>{obj.oper_profit} руб</b>')
    _oper_profit.short_description = 'Профит оператора'

    def _turnover(self, obj):
        return format_html(f'<b>{obj.turnover} руб</b>')
    _turnover.short_description = 'Общий оборот'

    def _turnover_orders(self, obj):
        return format_html(f'<b>{obj.orders_turnover} руб</b>')
    _turnover_orders.short_description = 'Оборот с обменов'

    def _turnover_transactions(self, obj):
        return format_html(f'<b>{obj.transactions_turnover} руб</b>')
    _turnover_transactions.short_description = 'Оборот ручных отправок'

    def volatility_btc(self, obj):
        return format_html(obj.volatility('BTC'))
    volatility_btc.short_description = 'BTC'

    def volatility_ltc(self, obj):
        return format_html(obj.volatility('LTC'))
    volatility_ltc.short_description = 'LTC'

    def volatility_xmr(self, obj):
        return format_html(obj.volatility('XMR'))
    volatility_xmr.short_description = 'XMR'

    def volatility_usdt(self, obj):
        return format_html(obj.volatility('USDT'))
    volatility_usdt.short_description = 'USDT'

    def _discount_info(self, obj):
        discount_info = obj.discount_info
        ul = f'''
            <ul style="margin-left: 0; padding-left: 0;">
                <li>Промокод: {discount_info["promocode"]} руб</li>
                <li>Бонусная заявка: {discount_info["bonus_discount"]} руб</li>
                <li>Рулетка: {discount_info["lucky"]} руб</li>
                <li>Кешбек: {discount_info["cashback"]} руб</li>
            </ul>
        '''

        return format_html(ul)
    _discount_info.short_description = 'Скидки'

    fieldsets = (
        ('Основная информация', {'fields': ('name', 'operator', 'start_time', 'end_time', 'night', 'volatility_btc', 'volatility_ltc', 'volatility_xmr', 'volatility_usdt')}),
        ('Статистика', {'fields': ('orders', 'transactions', 'purchases', '_turnover', '_turnover_orders', '_turnover_transactions', '_discount_info')}),
        ('Прибыль', {'fields': ('full_profit', 'bot_profit', '_oper_profit')})
    )

@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ['self_str', '_winner', 'amount', 'from_amount', 'start_time', 'end_time']

    def self_str(self, obj):
        return format_html(str(obj))
    self_str.short_description = ''

    def _winner(self, obj):
        if not obj.winner:
            return format_html('-')

        url = f'/admin/telegram/client/{obj.winner.id}/change/'
        return format_html(f'<a href="{url}">{obj.winner.tg_id}</a>')
    _winner.short_description = 'Победитель'

    def _clients(self, obj):
        url = obj.clients_url()
        return format_html(f'{len(obj.clients())} - <a href="{url}">Смотреть</a>')
    _clients.short_description = 'Участники'

    def has_add_permission(self, request, obj=None):
        if Competition.current():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def add_view(self, request, extra_content=None):
        self.readonly_fields = ['start_time', 'end_time', 'winner', 'self_str', '_clients', '_winner']
        self.fieldsets = (
            ('', {'fields': ('amount', 'from_amount')}),
        )
        return super(CompetitionAdmin, self).add_view(request)

    def change_view(self, request, object_id, extra_content=None):
        self.change_form_template = None
        self.readonly_fields = ['amount', 'from_amount', 'start_time', 'end_time', 'winner', 'self_str', '_clients', '_winner']
        obj = Competition.objects.get(id=object_id)
        if not obj.end_time:
            self.change_form_template = 'telegram/competition_admin.html'
        self.fieldsets = (
            ('', {'fields': ('winner', '_clients')}),
            ('', {'fields': ('start_time', 'end_time', 'amount', 'from_amount')})
        )
        return super(CompetitionAdmin, self).change_view(request, object_id)

    def response_change(self, request, obj):

        if "end-competition" in request.POST:
            if len(obj.clients()) > 0:
                obj.end()
                messages.add_message(request, messages.INFO, 'Конкурс завершен!')
            else:
                messages.add_message(request, messages.ERROR, 'В конкурсе не участвует ни один клиент!')
            return HttpResponseRedirect(f'/admin/telegram/competition/{obj.id}/change/')

        return super().response_change(request, obj)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        if change:
            context.update({
                'show_save': False,
                'show_save_and_continue': False,
                'show_save_and_add_another': False,
                'show_delete': False
            })
        else:
            context.update({
                'show_save': True,
                'show_save_and_continue': True,
                'show_save_and_add_another': False,
                'show_delete': False
            })
        return super().render_change_form(request, context, add, change, form_url, obj)


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['link', '_working_shift', 'bill_type', 'rub_value', 'pay_value']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def link(self, obj):
        url = f'/admin/telegram/bill/{obj.id}/change/'
        return format_html(f'<a href="{url}">Смотреть</a>')
    link.short_description = 'Действие'

    def _working_shift(self, obj):
        url = f'/admin/telegram/workingshift/{obj.working_shift.id}/change/'
        return format_html(f'<a href="{url}">{obj.working_shift}</a>')
    _working_shift.short_description = 'Смена'

    def get_readonly_fields(self, request, obj=None):
        if obj:
            self.readonly_fields = ['link', '_working_shift', 'bill_type', 'rub_value']
            if obj.working_shift.end_time:
                self.readonly_fields.append('pay_value')
        return self.readonly_fields

    fieldsets = (
        ('', {'fields': ('_working_shift', 'bill_type', 'rub_value', 'pay_value')}),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
	list_display = ['id', 'client', 'order']

	def has_add_permission(self, request, obj=None):
		return False
    
	def has_change_permission(self, request, obj=None):
		return False
    
	def has_delete_permission(self, request, obj=None):
		return False
    
	fieldsets = (
		('', {'fields': ('client', 'order', 'text')}),
	)


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ['id', '_working_shift', 'date', 'pay_value']
    readonly_fields = ['id', 'working_shift', 'date', 'purpose', 'pay_value']
    fieldsets = (
        ('', {'fields': ('id', 'working_shift', 'date', 'purpose', 'pay_value')}),
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def _working_shift(self, obj):
        if obj.working_shift:
            url = f'/admin/telegram/workingshift/{obj.working_shift.id}/change/'
            return format_html(f'<a href="{url}">{obj.working_shift}</a>')
        return '-'
    _working_shift.short_description = 'Смена'


@admin.register(OrderSell)
class OrderSellAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'client_tg_id', 'crypt_value', 'crypt', '_status', 'datetime']
    list_filter = ['crypt', 'status']
    search_fields = ['order_id', 'address']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_fields(self, request, obj=None):
        if obj and obj.recalculated_crypt_value and obj.recalculated_rub_value and obj.recalculated_pay_value_with_percent:
            return ['order_id', 'client', 'crypt', '_crypt_value', 'course', 'rub_value',
                    'pay_value_with_percent', 'recalculated_crypt_value', 'recalculated_rub_value',
                    'recalculated_pay_value_with_percent', 'address', 'payment_method', 'requisites',
                    'datetime', 'updated_datetime', 'status']
        else:
            return ['order_id', 'client', 'crypt', '_crypt_value', 'course', 'rub_value',
                    'pay_value_with_percent', 'address', 'payment_method', 'requisites', 'datetime',
                    'updated_datetime', 'status']

    def client_tg_id(self, obj):
        url = f'/admin/telegram/client/{obj.client.id}/change/'
        return format_html(f"<a href='{url}'>{obj.client.tg_id}</a>", url=url)
    
    def _crypt_value(self, obj):
        return format_html(f"{'{:.8f}'.format(obj.crypt_value).rstrip('0').rstrip('.')}")
    _crypt_value.short_description = 'Сумма в крипте'

    client_tg_id.short_description = 'Клиент'

    def _status(self, obj):
        return format_html(f'<span class="nowrap">{obj.get_status_display()}</span>')

    _status.short_description = 'Статус'

    def _datetime(self, obj):
        if obj.datetime:
            return format_html(f"{obj.datetime.strftime('%d-%m-%Y %H:%M:%S')}")
        else:
            return format_html(f"<p></p>")

    _datetime.short_description = 'Дата'

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['client', 'crypt', '_balance']
    list_filter = ['crypt']
    search_fields = ['client__tg_id', 'address']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description='Баланс', ordering='balance')
    def _balance(self, obj):
        return display_decimal(obj.balance)

    fieldsets = (
        (None, {'fields': ('client', 'crypt', 'address', '_balance')}),
    )


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['short_tx_id', 'client', 'category', '_amount', 'crypt', 'created_at']
    list_filter = ['wallet__crypt', 'category', 'internal', 'created_at']
    search_fields = ['wallet__client__tg_id', 'tx_id', 'address']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description='ID транзакции')
    def short_tx_id(self, obj):
        short_id = str(obj.tx_id).split('-')[0] + '...' + str(obj.tx_id).split('-')[-1]

        return format_html(f'<span class="nowrap">{short_id}</span>')

    @admin.display(description='Клиент')
    def client(self, obj):
        return str(obj.wallet.client.tg_id)

    @admin.display(description='Валюта', ordering='wallet__crypt__name')
    def crypt(self, obj):
        return obj.wallet.crypt.name

    @admin.display(description='Сумма', ordering='amount')
    def _amount(self, obj):
        return display_decimal(obj.amount)

    @admin.display(description='Комиссия', ordering='commission')
    def _commission(self, obj):
        return display_decimal(obj.commission)

    @admin.display(description='Комиссия провайдера', ordering='provider_commission')
    def _provider_commission(self, obj):
        return display_decimal(obj.provider_commission)

    @admin.display(description='Ссылка на обозреватель')
    def _explorer_link(self, obj):
        if obj.explorer_link is not None:
            return format_html(f'<a href="{obj.explorer_link}">{obj.explorer_link}</a>')

        return '-'

    fieldsets = (
        (None, {'fields': ('wallet', 'category', 'internal', 'tx_id', '_explorer_link', 'created_at')}),
        ('Информация о транзакции', {'fields': ('address', '_amount', '_commission', '_provider_commission')}),
    )


