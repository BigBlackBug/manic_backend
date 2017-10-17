from django.contrib import admin

from .models import Schedule, TimeSlot, Time, Master

admin.site.register(Master)
admin.site.register(Schedule)
admin.site.register(TimeSlot)
admin.site.register(Time)
