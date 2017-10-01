import io
import uuid
from datetime import timedelta

from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
from rest_framework.views import exception_handler


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
        return 'avatars/' + str(uuid.uuid4())

    @staticmethod
    def categories(instance, filename):
        return 'categories/' + str(uuid.uuid4())


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # TODO custom handler
    return response


def get_date(days: int):
    # TODO UNIFY DATE_FORMAT
    return (timezone.now() + timedelta(days=days)).strftime('%Y-%m-%d')
