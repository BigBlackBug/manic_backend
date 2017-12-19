"""_4hands2go URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

from src.apps.core.views import get_swagger_view

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^auth/', include('src.apps.authentication.urls')),
    url(r'^categories/', include('src.apps.categories.urls')),
    url(r'^masters/', include('src.apps.masters.urls')),
    url(r'^clients/', include('src.apps.clients.urls')),
    url(r'^orders/', include('src.apps.orders.urls')),
]\
+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
+ [
    url(r'^mgmt/auth/', include('src.apps.authentication.mgmt.urls')),
    url(r'^mgmt/categories/', include('src.apps.categories.mgmt.urls'))
]

if settings.DEBUG:
    urlpatterns.append(
        url(r'^docs/', get_swagger_view(title='4Hands2Go API Docs')), )
