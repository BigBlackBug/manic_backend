from django.conf.urls import url

from .views import ClientAvatarUpdateView, ClientCreateView, ClientUpdateView, Me, \
    AddPaymentCardView, DeletePaymentCardView

urlpatterns = [
    url(r'^$', ClientCreateView.as_view(), name=ClientCreateView.view_name),
    url(r'^me$', Me.as_view(), name=Me.view_name),
    url(r'^(?P<pk>[0-9]+)$', ClientUpdateView.as_view(), name=ClientUpdateView.view_name),
    url(r'^(?P<pk>[0-9]+)/avatar$', ClientAvatarUpdateView.as_view(),
        name=ClientAvatarUpdateView.view_name),
    url(r'^(?P<pk>[0-9]+)/payment_card$', AddPaymentCardView.as_view(),
        name=AddPaymentCardView.view_name),
    url(r'^(?P<pk>[0-9]+)/payment_card/(?P<card_id>[0-9]+)$', DeletePaymentCardView.as_view(),
        name=DeletePaymentCardView.view_name),
]
