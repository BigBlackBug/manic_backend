from django.conf.urls import url

from .views import OrderListCreateView, CancelOrderView, CompleteOrderView

urlpatterns = [
    url(r'^$', OrderListCreateView.as_view(),
        name=OrderListCreateView.view_name),
    url(r'^(?P<pk>[0-9]+)$', CancelOrderView.as_view(),
        name=CancelOrderView.view_name),
    url(r'^(?P<pk>[0-9]+)/complete$', CompleteOrderView.as_view(),
        name=CompleteOrderView.view_name),
]
