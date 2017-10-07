from django.conf.urls import url

from .views import OrderCreateView

urlpatterns = [
    url(r'^$', OrderCreateView.as_view(), name=OrderCreateView.view_name),
    # url(r'^(?P<pk>[0-9]+)$', ClientDetailView.as_view(), name=ClientDetailView.view_name),
]
