from django.contrib import admin

from src.apps.orders.models import CloudPaymentsTransaction

admin.site.register(CloudPaymentsTransaction)
