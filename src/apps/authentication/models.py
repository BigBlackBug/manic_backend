import binascii
import os

from django.db import models
from django.utils.translation import ugettext_lazy as _

from src.apps.core.utils import Folders
from .utils import Gender


class Registration(models.Model):
    """
    A temporary class that represents application login/registration process
    """
    phone = models.CharField(max_length=40, unique=True)
    verification_code = models.CharField(max_length=4)

    # TODO create a cron which cleans up expired registrations
    expires = models.DateTimeField()

    def __str__(self):
        return f'Phone: {self.phone}, expires: {self.expires}, ' \
               f'code: {self.verification_code}'


class PhoneAuthUser(models.Model):
    """
    A base class for a User who's authenticated through a phone number
    """
    phone = models.CharField(max_length=40, unique=True)

    def is_client(self):
        try:
            self.client
        except AttributeError as e:
            return False
        else:
            return True

    def is_master(self):
        try:
            self.master
        except AttributeError as e:
            return False
        else:
            return True

    def has_account(self):
        return self.is_client() or self.is_master()

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

    def __str__(self):
        return self.phone


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


class UserProfile(models.Model):
    user = models.OneToOneField(PhoneAuthUser,
                                related_name="%(class)s",
                                related_query_name="%(class)s", )

    first_name = models.CharField(max_length=32)
    avatar = models.ImageField(upload_to=Folders.avatars, blank=True, null=True)

    gender = models.CharField(
        max_length=1,
        choices=Gender.CHOICES,
        default=Gender.FEMALE,
    )

    date_of_birth = models.DateField()

    # FK fields
    # debit_cards

    class Meta:
        abstract = True
