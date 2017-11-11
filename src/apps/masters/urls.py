from django.conf.urls import url

from .views import MasterListView, MasterDetailView, \
    MasterSearchView, MasterBestMatchView, AddPortfolioItemsView, \
    CreateDeleteScheduleView, MeMasterView

urlpatterns = [
    url(r'^$', MasterListView.as_view(), name=MasterListView.view_name),
    url(r'^me$', MeMasterView.as_view(), name=MeMasterView.view_name),
    url(r'^search$', MasterSearchView.as_view(),
        name=MasterSearchView.view_name),
    url(r'^best_match$', MasterBestMatchView.as_view(),
        name=MasterBestMatchView.view_name),
    url(r'^(?P<pk>[0-9]+)$', MasterDetailView.as_view(),
        name=MasterDetailView.view_name),
    url(r'^(?P<pk>[0-9]+)/portfolio', AddPortfolioItemsView.as_view(),
        name=AddPortfolioItemsView.view_name),
    url(r'^(?P<pk>[0-9]+)/schedule', CreateDeleteScheduleView.as_view(),
        name=CreateDeleteScheduleView.view_name),
]
