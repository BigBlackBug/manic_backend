import binascii
import os
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from sphinx.locale import _


class Registration(models.Model):
    REGISTRATION_LIFETIME = timedelta(minutes=5)

    phone = models.CharField(max_length=40, unique=True)
    verification_code = models.CharField(max_length=4)
    expires = models.DateTimeField(editable=False, default=timezone.now() + REGISTRATION_LIFETIME)


class PhoneAuthUser(models.Model):
    """
    A base class for a User who's authenticated through a phone number
    """
    phone = models.CharField(max_length=40, unique=True)

    @property
    def is_active(self):
        """
        Always returns True.
        """
        return True

    @property
    def is_anonymous(self):
        """
        Always return False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True


class Token(models.Model):
    """
    The default authorization token model.
    """
    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    user = models.OneToOneField(
        PhoneAuthUser, related_name='auth_token',
        on_delete=models.CASCADE, verbose_name=_("User")
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        # Work around for a bug in Django:
        # https://code.djangoproject.com/ticket/19422
        #
        # Also see corresponding ticket:
        # https://github.com/encode/django-rest-framework/issues/705
        abstract = 'rest_framework.authtoken' not in settings.INSTALLED_APPS
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key
