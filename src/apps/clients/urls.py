from django.conf.urls import url

from .views import ClientAvatarUpdateView, ClientCreateView, ClientUpdateView, \
    MeClient, AddPaymentCardView, DeletePaymentCardView, AddAddressView, \
    AddressUpdateView, CreateComplaintView

urlpatterns = [
    url(r'^$', ClientCreateView.as_view(), name=ClientCreateView.view_name),
    url(r'^me$', MeClient.as_view(), name=MeClient.view_name),
    url(r'^(?P<pk>[0-9]+)$', ClientUpdateView.as_view(),
        name=ClientUpdateView.view_name),
    url(r'^(?P<pk>[0-9]+)/avatar$', ClientAvatarUpdateView.as_view(),
        name=ClientAvatarUpdateView.view_name),
    url(r'^(?P<pk>[0-9]+)/payment_cards$', AddPaymentCardView.as_view(),
        name=AddPaymentCardView.view_name),
    url(r'^(?P<pk>[0-9]+)/complaints$', CreateComplaintView.as_view(),
        name=CreateComplaintView.view_name),
    url(r'^(?P<pk>[0-9]+)/payment_cards/(?P<card_id>[0-9]+)$',
        DeletePaymentCardView.as_view(),
        name=DeletePaymentCardView.view_name),
    url(r'^(?P<pk>[0-9]+)/addresses$', AddAddressView.as_view(),
        name=AddAddressView.view_name),
    url(r'^(?P<pk>[0-9]+)/addresses/(?P<address_id>[0-9]+)$',
        AddressUpdateView.as_view(),
        name=AddressUpdateView.view_name),
]
