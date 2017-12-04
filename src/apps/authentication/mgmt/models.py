import binascii
import os

from django.db import models
from django.utils.translation import ugettext_lazy as _

from src.apps.authentication.utils import get_admin_user_model


class AdminToken(models.Model):
    """
    Yes, a separate model for Admin App Authentication
    """
    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    user = models.OneToOneField(
        get_admin_user_model(), related_name='auth_token',
        on_delete=models.CASCADE, verbose_name=_("User")
    )

    class Meta:
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key
