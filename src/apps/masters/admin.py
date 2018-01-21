from django.contrib import admin

from .models import Schedule, TimeSlot, Master, Feedback, PortfolioImage, \
    Balance

admin.site.register(Master)
admin.site.register(Balance)
admin.site.register(Schedule)
admin.site.register(TimeSlot)
admin.site.register(Feedback)
admin.site.register(PortfolioImage)
