from rest_framework import filters

from src.apps.orders.models import OrderItem


class ClientSearchFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        qs = super().filter_queryset(request, queryset, view)
        service = request.query_params.get('service', None)
        if service:
            # TODO shitty, but at the moment I don't care
            items = OrderItem.objects.filter(service__pk=service). \
                select_related('order__client')
            return qs.filter(id__in=[item.order.client.id for item in items])
        return super().filter_queryset(request, queryset, view)
