from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


class InterfaceMeta(type):
    """
    A kinda dirty hack which allows to have a
    view_name attribute in each subclass of NamedAPIView.
    All because I'm tired of manual naming.

    * You should not use the same view class for multiple endpoints.
      You probably wouldn't anyway, but this would break the hack.
    """

    def __new__(cls, name, parents, dct):
        parents_names = [f'{p.__module__}.{p.__qualname__}' for p in parents]
        if f'{__name__}.NamedAPIView' in parents_names:
            dct['view_name'] = dct['__module__'] + '.' + dct['__qualname__']

        return super(InterfaceMeta, cls).__new__(cls, name, parents, dct)


class NamedAPIView(APIView, metaclass=InterfaceMeta):
    view_name = None
    permission_classes = (IsAuthenticated,)

    def get_exception_handler(self):
        return super().get_exception_handler()
