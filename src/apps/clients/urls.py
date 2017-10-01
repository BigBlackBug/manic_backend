from django.conf.urls import url

from .views import ClientAvatarUpdateView, ClientCreateView, ClientUpdateView

urlpatterns = [
    url(r'^$', ClientCreateView.as_view(), name=ClientCreateView.view_name),
    url(r'^(?P<pk>[0-9])$', ClientUpdateView.as_view(), name=ClientUpdateView.view_name),
    url(r'^(?P<pk>[0-9]+)/avatar$', ClientAvatarUpdateView.as_view(),
        name=ClientAvatarUpdateView.view_name),
    # url(r'^(?P<pk>[0-9]+)$', ClientDetailView.as_view(), name=ClientDetailView.view_name),
]
