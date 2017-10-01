from datetime import timedelta

from django.utils import timezone


def get_date(days: int):
    # TODO UNIFY DATE_FORMAT
    return (timezone.now() + timedelta(days=days)).strftime('%Y-%m-%d')
