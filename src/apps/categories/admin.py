from django.contrib import admin

# Register your models here.
from .models import ServiceCategory, Service, DisplayItem

admin.site.register(DisplayItem)
admin.site.register(ServiceCategory)
admin.site.register(Service)
