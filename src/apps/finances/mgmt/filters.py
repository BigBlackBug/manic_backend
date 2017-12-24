from rest_framework import filters


class TransactionEntryListSearchFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        entry_type = request.query_params.get('entry_type', None)
        if entry_type:
            queryset = queryset.filter(entry_type=entry_type)
        return super().filter_queryset(request, queryset, view)
