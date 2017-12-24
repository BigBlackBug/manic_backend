from django.conf.urls import url

from src.apps.categories.mgmt.views import MgmtUpdateDeleteServiceCategoryView, \
    MgmtListCreateServiceCategoryView, MgmtCreateServiceView, \
    MgmtUpdateDeleteServiceView, MgmtListCreateDisplayItemView, \
    MgmtUpdateDeleteDisplayItemView
from ..views import ServiceListView

urlpatterns = [
    url(r'^$', MgmtListCreateServiceCategoryView.as_view(),
        name=MgmtListCreateServiceCategoryView.view_name),
    url(r'^(?P<pk>[0-9]+)$', MgmtUpdateDeleteServiceCategoryView.as_view(),
        name=MgmtUpdateDeleteServiceCategoryView.view_name),

    url(r'^(?P<pk>[0-9]+)/services$', MgmtCreateServiceView.as_view(),
        name=MgmtCreateServiceView.view_name),
    url(r'^(?P<pk>[0-9]+)/services/(?P<service_id>[0-9]+)$',
        MgmtUpdateDeleteServiceView.as_view(),
        name=MgmtUpdateDeleteServiceView.view_name),

    url(r'^display_items$', MgmtListCreateDisplayItemView.as_view(),
        name=MgmtListCreateDisplayItemView.view_name),
    url(r'^display_items/(?P<pk>[0-9]+)$',
        MgmtUpdateDeleteDisplayItemView.as_view(),
        name=MgmtUpdateDeleteDisplayItemView.view_name),

    url(r'^services$', ServiceListView.as_view(),
        name=ServiceListView.view_name),
]
