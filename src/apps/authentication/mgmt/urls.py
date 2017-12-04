from django.conf.urls import url

from .views import MgmtLoginView

urlpatterns = [
    url(r'^login/$', MgmtLoginView.as_view(), name=MgmtLoginView.view_name),
]
