from django.conf.urls import url

from .views import DisplayItemList

urlpatterns = [
    url(r'^display_items/$', DisplayItemList.as_view(), name=DisplayItemList.view_name),
    # url(r'^categories/(?P<service_id>[0-9]+)/image/$', ServiceCategoryImageView.as_view(),
    #     name=ServiceCategoryImageView.view_name)
]
