from django.conf.urls import url

from .views import Logout, CreateRegistrationView, UpdateRegistrationView

urlpatterns = [
    url(r'^logout/', Logout.as_view(), name='logout'),
    url(r'^registrations/$', CreateRegistrationView.as_view(),
        name=CreateRegistrationView.view_name),
    url(r'^registrations/(?P<reg_id>[0-9]+)/$', UpdateRegistrationView.as_view(),
        name=UpdateRegistrationView.view_name),
]
