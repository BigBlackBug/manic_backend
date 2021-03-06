import datetime

from django.utils import timezone


def get_default_date_range(range_days=14):
    """
    Returns a tuple with default date range (2 weeks from now)
    :return:
    """
    #TODO timezone fails
    now = timezone.now()
    return now.date(), now.date() + datetime.timedelta(days=range_days)
