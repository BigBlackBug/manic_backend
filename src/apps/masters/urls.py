from django.conf.urls import url

from src.apps.masters.views import MastersView

urlpatterns = [
    url(r'^$', MastersView.as_view(), name=MastersView.view_name),
]
