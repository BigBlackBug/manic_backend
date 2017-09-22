import io
import uuid

from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile


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
    def avatars(instance, filename):
        return 'avatars/' + str(uuid.uuid4())

    @staticmethod
    def categories(instance, filename):
        return 'categories/' + str(uuid.uuid4())
