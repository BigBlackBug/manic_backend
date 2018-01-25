from django.conf.urls import url

from .views import ListCreateTextView

urlpatterns = [
    url(r'^$', ListCreateTextView.as_view(), name=ListCreateTextView.view_name),
]
