import io
import uuid
from datetime import timedelta

from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
from rest_framework import status, exceptions
from rest_framework.compat import set_rollback
from rest_framework.response import Response
from rest_framework.views import exception_handler

from src.apps.core.exceptions import ApplicationError


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

        # TODO error_type
        return Response(data={
            'error_type': None,
            'detail': detail
        }, status=exc.status_code, headers=headers)
    elif isinstance(exc, ApplicationError):
        set_rollback()
        if len(exc.args) == 1:
            parent_exc = exc.args[0]
            message = str(parent_exc)
        else:
            message = None
        response = Response(data={
            'erorr_type': None,
            'detail': message
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return exception_handler(exc, context)

    return response


def get_date(days: int):
    # TODO UNIFY DATE_FORMAT
    return (timezone.now() + timedelta(days=days)).strftime('%Y-%m-%d')
