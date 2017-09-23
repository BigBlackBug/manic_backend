from django.contrib import admin

from .models import PhoneAuthUser, Registration, Token

admin.site.register(PhoneAuthUser)
admin.site.register(Registration)
admin.site.register(Token)
