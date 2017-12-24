from django.conf.urls import url

from .views import DisplayItemListView, CategoryListView

urlpatterns = [
    url(r'^$', CategoryListView.as_view(),
        name=CategoryListView.view_name),
    url(r'^display_items/$', DisplayItemListView.as_view(),
        name=DisplayItemListView.view_name),
]
