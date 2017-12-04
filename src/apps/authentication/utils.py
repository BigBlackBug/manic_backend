from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class Gender:
    MALE = 'M'
    FEMALE = 'F'
    CHOICES = (
        (MALE, 'Мужчина'),
        (FEMALE, 'Женщина'),
    )


def get_admin_user_model():
    """
    Returns the Admin User model that is active in this project.
    """
    try:
        return django_apps.get_model(settings.ADMIN_APP_USER,
                                     require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            "AUTH_USER_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "AUTH_USER_MODEL refers to model '%s' that has not been installed" % settings.AUTH_USER_MODEL
        )
