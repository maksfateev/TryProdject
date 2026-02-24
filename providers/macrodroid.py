from general_settings.models import Card
from django.db.models import Q, F

import random


class Client:
    def __init__(self):
        pass

    class RequestException(Exception):
        pass

    class TimeOutException(Exception):
        pass

    def create_p2p_order(self, amount, reqs_type):
        cards = Card.objects.filter(Q(status='worked_all') | Q(status=f'worked_{reqs_type}'))
        cards = cards.exclude(Q(trader__in_work=False) | Q(trader__balance__lt=amount)).order_by('count')

        if not cards.exists():
            raise self.TimeOutException()

        #card = random.choice(list(cards))
        card = cards.first()
        Card.objects.filter(id=card.id).update(count=F('count') + 1)

        data = {'bank': card.bank}

        if reqs_type == 'card':
            data['reqs'] = card.card_number
        else:
            data['reqs'] = card.phone_number

        data['label'] = card.id

        return data