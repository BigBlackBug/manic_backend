from enum import Enum

from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class ApplicationError(Exception):
    class ErrorTypes(Enum):
        UNEXPECTED_ERROR = -1
        SMS_ERROR = 100
        PAYMENT_ERROR = 200
        APPLICATION_ERROR = 300
        ORDER_CREATION_ERROR = 310
        ORDER_START_TOO_EARLY = 320
        ORDER_START_WRONG_DAY = 321

    def __init__(self, *args,
                 error_type: ErrorTypes = ErrorTypes.UNEXPECTED_ERROR):
        super().__init__(*args)
        self.error_code = error_type and error_type.value


class NoContentError(APIException):
    status_code = status.HTTP_204_NO_CONTENT
    default_detail = _('No content')
    default_code = 'error'
