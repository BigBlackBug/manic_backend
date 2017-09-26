import django_filters

from .models import Master


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class MasterListFilter(django_filters.FilterSet):
    # date_0=2017-09-20, date_1=2017-10-20
    date = django_filters.DateFromToRangeFilter(name='schedule__date')
    # service_in=1,2,3,4
    service_in = NumberInFilter(name='services__id', lookup_expr='in')

    # TODO maybe filter out unavailable time slots?
    # time_0=12:30, time_1=15:30
    time = django_filters.TimeRangeFilter(name='schedule__time_slots__time__value')

    class Meta:
        model = Master
        fields = ['date', 'time', 'service_in']
