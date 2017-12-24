from django.conf.urls import url

from src.apps.masters.mgmt.views import MgmtMasterSearchView, \
    MgmtMasterDetailUpdateView, MgmtMasterAvatarUpdateView, \
    MgmtUpdatePortfolioStatusView

urlpatterns = [
    url(r'^$', MgmtMasterSearchView.as_view(),
        name=MgmtMasterSearchView.view_name),
    url(r'^(?P<pk>[0-9]+)$', MgmtMasterDetailUpdateView.as_view(),
        name=MgmtMasterSearchView.view_name),
    url(r'^(?P<pk>[0-9]+)/avatar$', MgmtMasterAvatarUpdateView.as_view(),
        name=MgmtMasterAvatarUpdateView.view_name),
    url(r'^(?P<pk>[0-9]+)/portfolio/(?P<portfolio_id>[0-9]+)$',
        MgmtUpdatePortfolioStatusView.as_view(),
        name=MgmtUpdatePortfolioStatusView.view_name),
]
