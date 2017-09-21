from django.conf.urls import url

from .views import ServiceCategoryList

urlpatterns = [
    url(r'^$', ServiceCategoryList.as_view(), name=ServiceCategoryList.view_name),
    # url(r'^categories/(?P<service_id>[0-9]+)/image/$', ServiceCategoryImageView.as_view(),
    #     name=ServiceCategoryImageView.view_name)
]
