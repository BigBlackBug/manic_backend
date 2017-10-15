import datetime
from django.utils import timezone


def get_default_date_range():
    """
    Retunrs a tuple with default date range (2 weeks from now)
    :return:
    """
    now = timezone.now()
    return now.date(), now.date() + datetime.timedelta(days=14)