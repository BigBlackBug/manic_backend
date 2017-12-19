from django.conf.urls import url

from ..views import CategoryListView, DisplayItemList, \
    ServiceListView

urlpatterns = [
    url(r'^$', CategoryListView.as_view(),
        name=CategoryListView.view_name),
    url(r'^display_items$', DisplayItemList.as_view(),
        name=DisplayItemList.view_name),
    url(r'^services$', ServiceListView.as_view(),
        name=ServiceListView.view_name),
]
