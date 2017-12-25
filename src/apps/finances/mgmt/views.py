from rest_framework import generics
from rest_framework.filters import OrderingFilter

from src.apps.core.permissions import IsAdmin
from src.apps.finances.mgmt.filters import TransactionEntryListSearchFilter
from src.apps.finances.mgmt.serializers import TransactionEntrySerializer
from src.apps.finances.models import TransactionEntry


class TransactionEntryListView(generics.ListAPIView):
    view_name = 'tx-entry-list'
    queryset = TransactionEntry.objects.all()
    serializer_class = TransactionEntrySerializer
    permission_classes = (IsAdmin,)
    filter_backends = (TransactionEntryListSearchFilter, OrderingFilter)
    search_fields = ('^master__first_name',)
    ordering = ('date',)

    def get(self, request, *args, **kwargs):
        """
        Returns a list of transaction entries to be displayed
        in the mgmt search page.

        Query Params:

        ```search``` - searches by master's first_name

        ```entry_type``` - searches for entries with this type.

        Can be IN or OUT.

        IN means transaction from a client to the 4hands account.
        OUT means payment from the 4hands account to a master.

        Response:
        200 OK
        ```
        [{
          'id': 1,
          'master':{
            'first_name': 'Maria',
            'id':10
          },
          'date': '2017-10-23',
          'entry_type': 'IN/OUT',
          'value': 1500,
          //order_id
          'order': 3
        }]
        ```
        """
        return super().get(request, *args, **kwargs)
