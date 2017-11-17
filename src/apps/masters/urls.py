from django.conf.urls import url

from .views import MasterListCreateView, MasterDetailUpdateView, \
    MasterSearchView, MasterBestMatchView, AddPortfolioItemsView, \
    CreateDeleteScheduleView, MeMasterView, AddPortfolioItemDescriptionView, \
    MasterAvatarUpdateView, AddFeedbackView

urlpatterns = [
    url(r'^$', MasterListCreateView.as_view(),
        name=MasterListCreateView.view_name),
    url(r'^me$', MeMasterView.as_view(), name=MeMasterView.view_name),
    url(r'^search$', MasterSearchView.as_view(),
        name=MasterSearchView.view_name),
    url(r'^best_match$', MasterBestMatchView.as_view(),
        name=MasterBestMatchView.view_name),
    url(r'^(?P<pk>[0-9]+)$', MasterDetailUpdateView.as_view(),
        name=MasterDetailUpdateView.view_name),
    url(r'^(?P<pk>[0-9]+)/avatar$', MasterAvatarUpdateView.as_view(),
        name=MasterAvatarUpdateView.view_name),
    url(r'^(?P<pk>[0-9]+)/feedback$', AddFeedbackView.as_view(),
        name=AddFeedbackView.view_name),
    url(r'^(?P<pk>[0-9]+)/portfolio_descriptions$',
        AddPortfolioItemDescriptionView.as_view(),
        name=AddPortfolioItemDescriptionView.view_name),
    url(r'^(?P<pk>[0-9]+)/portfolio$', AddPortfolioItemsView.as_view(),
        name=AddPortfolioItemsView.view_name),
    url(r'^(?P<pk>[0-9]+)/schedule$', CreateDeleteScheduleView.as_view(),
        name=CreateDeleteScheduleView.view_name),
]
