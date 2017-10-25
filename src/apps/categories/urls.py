from django.conf.urls import url

from .views import DisplayItemList

urlpatterns = [
    url(r'^display_items/$', DisplayItemList.as_view(),
        name=DisplayItemList.view_name),
]
