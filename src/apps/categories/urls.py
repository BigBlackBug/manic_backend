from django.conf.urls import url

from .views import DisplayItemList, CategoryListView

urlpatterns = [
    url(r'^$', CategoryListView.as_view(),
        name=CategoryListView.view_name),
    url(r'^display_items/$', DisplayItemList.as_view(),
        name=DisplayItemList.view_name),
]
