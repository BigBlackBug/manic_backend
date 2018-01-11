from django.conf.urls import url

from src.apps.devices.views import FCMAddDeviceView

urlpatterns = [
    url(r'^$', FCMAddDeviceView.as_view(), name=FCMAddDeviceView.view_name),
]
