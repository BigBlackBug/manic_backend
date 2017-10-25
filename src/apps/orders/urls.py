from django.conf.urls import url

from .views import OrderListCreateView, CancelOrderView

urlpatterns = [
    url(r'^$', OrderListCreateView.as_view(),
        name=OrderListCreateView.view_name),
    url(r'^(?P<pk>[0-9]+)$', CancelOrderView.as_view(),
        name=CancelOrderView.view_name),
]
