from django.conf.urls import url

from src.apps.devices.views import FCMDeviceViewSet

urlpatterns = [
    url(r'^$', FCMDeviceViewSet.as_view(), name=FCMDeviceViewSet.view_name),
]
