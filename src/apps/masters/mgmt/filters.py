from rest_framework import filters


class MasterListSearchFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        service = request.query_params.get('service', None)
        if service:
            queryset = queryset.filter(services__id__in=service)
        return super().filter_queryset(request, queryset, view)
