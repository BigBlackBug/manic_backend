from django.conf.urls import url

from .views import LogoutView, CreateRegistrationView, UpdateRegistrationView

urlpatterns = [
    url(r'^logout/$', LogoutView.as_view(), name=LogoutView.view_name),
    url(r'^registrations/$', CreateRegistrationView.as_view(),
        name=CreateRegistrationView.view_name),
    url(r'^registrations/(?P<reg_id>[0-9]+)/$', UpdateRegistrationView.as_view(),
        name=UpdateRegistrationView.view_name),
]
