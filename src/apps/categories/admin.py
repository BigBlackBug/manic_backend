from django.contrib import admin

# Register your models here.
from .models import ServiceCategory, Service

admin.site.register(ServiceCategory)
admin.site.register(Service)
