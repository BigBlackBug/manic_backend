from django.conf.urls import url

from .views import ClientListView

urlpatterns = [
    url(r'^$', ClientListView.as_view(), name=ClientListView.view_name),
]
