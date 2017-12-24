from django.conf.urls import url

from .views import TransactionEntryListView

urlpatterns = [
    url(r'^$', TransactionEntryListView.as_view(),
        name=TransactionEntryListView.view_name),
]
