from django.conf.urls import url

from src.apps.devices.views import FCMAddDeviceView, FCMRemoveDeviceView

urlpatterns = [
    url(r'^$', FCMAddDeviceView.as_view(), name=FCMAddDeviceView.view_name),
    url(r'^(?P<pk>[0-9]+)$', FCMRemoveDeviceView.as_view(),
        name=FCMRemoveDeviceView.view_name),
]
