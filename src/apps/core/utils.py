import io
import logging
import uuid
from datetime import timedelta

from PIL import Image
from cloudpayments import CloudPaymentsError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
from rest_framework import status, exceptions
from rest_framework.compat import set_rollback
from rest_framework.response import Response
from rest_framework.views import exception_handler

from src.apps.core.exceptions import ApplicationError

logger = logging.getLogger(__name__)

# TODO make a separate handler for payment exception logging
payment_logger = logging.getLogger(__name__)


def make_in_memory_image(filename):
    img = Image.new('RGB', size=(16, 16))
    buffer = io.BytesIO()
    img.save(fp=buffer, format='JPEG')

    buff_val = buffer.getvalue()
    f = ContentFile(buff_val)
    return InMemoryUploadedFile(f, None, filename, 'image/jpeg',
                                f.tell, None)


class Folders:
    @staticmethod
    def portfolio(instance, filename):
        return f'portfolio/{instance.master.id}/{uuid.uuid4()}'

    @staticmethod
    def avatars(instance, filename):
        return f'avatars/{str(uuid.uuid4())}'

    @staticmethod
    def categories(instance, filename):
        return f'categories/{str(uuid.uuid4())}'

    @staticmethod
    def display_items(instance, filename):
        return f'display_items/{str(uuid.uuid4())}'


def custom_exception_handler(exc, context):
    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        set_rollback()

        # most of the time there will be a single message
        # coming from ValidationError
        detail = exc.detail
        if isinstance(detail, list) and len(detail) == 1:
            detail = detail[0]

        logger.exception(f'Unexpected APIException')

        # TODO error_type
        return Response(data={
            'error_code': ApplicationError.ErrorTypes.UNEXPECTED_ERROR.value,
            'detail': detail
        }, status=exc.status_code, headers=headers)
    elif isinstance(exc, ApplicationError):
        set_rollback()
        if len(exc.args) == 1:
            parent_exc = exc.args[0]
            message = str(parent_exc)
        else:
            message = None
        logger.exception(f'Unexpected ApplicationError')

        return Response(data={
            'error_code': exc.error_code,
            'detail': message
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    elif isinstance(exc, CloudPaymentsError):
        set_rollback()
        if len(exc.args) == 1:
            parent_exc = exc.args[0]
            message = str(parent_exc)
        else:
            message = None

        payment_logger.exception(f'Unexpected CloudPaymentsException')

        return Response(data={
            'error_code': ApplicationError.ErrorTypes.PAYMENT_ERROR.value,
            'detail': message
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return exception_handler(exc, context)


def get_date(days: int):
    # TODO UNIFY DATE_FORMAT
    return (timezone.now() + timedelta(days=days)).strftime('%Y-%m-%d')


def get_ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    return ip_address
