from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class ApplicationError(Exception):
    pass


class NoContentError(APIException):
    status_code = status.HTTP_204_NO_CONTENT
    default_detail = _('No content')
    default_code = 'error'
