from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import CoreJSONRenderer
from rest_framework.response import Response
from rest_framework.schemas import SchemaGenerator
from rest_framework.views import APIView
from rest_framework_swagger import renderers


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


def get_swagger_view(title=None, url=None, patterns=None, urlconf=None):
    """
    Returns schema view which renders Swagger/OpenAPI.
    """

    class SwaggerSchemaView(APIView):
        _ignore_model_permissions = True
        exclude_from_schema = True
        permission_classes = [AllowAny]
        renderer_classes = [
            CoreJSONRenderer,
            renderers.OpenAPIRenderer,
            renderers.SwaggerUIRenderer
        ]

        def get(self, request):
            generator = SchemaGenerator(
                title=title,
                url=url,
                patterns=patterns,
                urlconf=urlconf
            )
            schema = generator.get_schema(public=True)

            if not schema:
                raise ValidationError(
                    'The schema generator did not return a schema Document'
                )

            return Response(schema)

    return SwaggerSchemaView.as_view()
