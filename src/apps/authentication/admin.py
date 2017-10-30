from django.contrib import admin

from .models import PhoneAuthUser, Registration, Token


class RegistrationAdmin(admin.ModelAdmin):
    readonly_fields = ('expires',)


admin.site.register(PhoneAuthUser)
admin.site.register(Registration, RegistrationAdmin)
admin.site.register(Token)
