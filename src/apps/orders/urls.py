from django.conf.urls import url

from .views import CancelOrderView, CompleteOrderView, OrderListCreateView
from .views_payment import PayForOrderView, FinishS3DView, \
    CloudPaymentsTransactionView

urlpatterns = [
    url(r'^$', OrderListCreateView.as_view(),
        name=OrderListCreateView.view_name),
    url(r'^(?P<pk>[0-9]+)$', CancelOrderView.as_view(),
        name=CancelOrderView.view_name),
    url(r'^(?P<pk>[0-9]+)/pay$', PayForOrderView.as_view(),
        name=PayForOrderView.view_name),
    url(r'^confirm_3ds$', FinishS3DView.as_view(),
        name=FinishS3DView.view_name),
    url(r'^(?P<pk>[0-9]+)/complete$', CompleteOrderView.as_view(),
        name=CompleteOrderView.view_name),
    url(r'^cloudpayments_transaction/(?P<transaction_id>[0-9]+)$',
        CloudPaymentsTransactionView.as_view(),
        name=CloudPaymentsTransactionView.view_name),
]
