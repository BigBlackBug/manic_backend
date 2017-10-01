from django.conf.urls import url

from src.apps.masters.views import MasterListView, MasterDetailView, MasterScheduleView, \
    MasterSearchView

urlpatterns = [
    url(r'^$', MasterListView.as_view(), name=MasterListView.view_name),
    url(r'^search$', MasterSearchView.as_view(), name=MasterSearchView.view_name),
    url(r'^(?P<pk>[0-9]+)$', MasterDetailView.as_view(), name=MasterDetailView.view_name),
    url(r'^(?P<pk>[0-9]+)/schedule$', MasterScheduleView.as_view(),
        name=MasterScheduleView.view_name),
]
