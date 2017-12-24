from rest_framework import generics, mixins, parsers, status
from rest_framework.exceptions import NotFound
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from src.apps.core.permissions import IsAdmin
from src.apps.core.serializers import ImageSerializer
from .filters import MasterListSearchFilter
from .serializers import MgmtMasterListSerializer, \
    MgmtMasterUpdateSerializer
from ..models import Master, PortfolioImage
from ..serializers import MasterSerializer
from ..views import MasterDetailUpdateView


class MgmtMasterSearchView(generics.ListAPIView):
    view_name = 'mgmt-master-list'
    queryset = Master.objects.all()
    serializer_class = MgmtMasterListSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (MasterListSearchFilter, OrderingFilter)
    search_fields = ('^first_name', '=id', '^user__phone', '^email')
    ordering = ('first_name',)

    def get(self, request, *args, **kwargs):
        """
        Returns a list of masters to be displayed
        in the mgmt search page.

        Query Params: ```search, service```

        Search Params: ```first_name, id, phone, email```

        Response:
        200 OK
        ```
        [{
          'id': 1,
          'first_name': 'Maria',
          'status': 'VERIFIED',
          'phone': '88005553535',
          'email': 'good@one.com',
          'balance':{
            'future':10,
            'on_hold':0,
            'transferred':1000
          },
        }]
        ```
        """
        return super().get(request, *args, **kwargs)


class MgmtMasterDetailUpdateView(MasterDetailUpdateView):
    view_name = 'mgmt-detail-update-master'
    queryset = Master.objects.all()
    permission_classes = (IsAdmin,)
    serializer_class = MasterSerializer

    def get_permissions(self):
        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        if not self.request:
            # TODO this is a fucking bug of the schema generation module
            return MasterSerializer

        if self.request.method == 'PATCH':
            return MgmtMasterUpdateSerializer
        return MasterSerializer

    def patch(self, request, *args, **kwargs):
        """
        Updates a master's status

        Input:
        ```
        {
          'first_name':'Maria',
          'date_of_birth':'1980-10-20',
          'email':'supercool@master.com',
          'gender':'F',
          'about': 'I am super cool',
          'services':'1,2,3,4',
          'location': {'lat':10, 'lon':12}
          'status': 'ON_REVIEW/DELETED/BLOCKED/VERIFIED'
        }
        ```

        Response:

        200 OK

        """
        self.partial_update(request, *args, **kwargs)
        return Response(data={})
        # def get(self, request, *args, **kwargs):
        #     return super().get(request, *a)


class MgmtMasterAvatarUpdateView(mixins.UpdateModelMixin,
                                 mixins.DestroyModelMixin,
                                 generics.GenericAPIView):
    view_name = 'mgmt-master-avatar-update'

    parser_classes = (parsers.MultiPartParser,)
    permission_classes = (IsAdmin,)
    queryset = Master.objects.all()
    serializer_class = ImageSerializer

    def delete(self, request, *args, **kwargs):
        """
        Deletes an avatar of the master

        Response:

        204 No Content
        """
        master = self.get_object()
        master.avatar.delete()
        master.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, *args, **kwargs):
        """
        Adds or replaces the avatar of the master

        Input:

        multi-part form data where `image` field contains the image

        Response:
        201 Created `{'image':'url-to-the-image'}`

        400 Bad Request
        """
        master = self.get_object()
        serializer = ImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image = serializer.validated_data['image']
        master.avatar = image
        master.save()

        return Response(status=status.HTTP_201_CREATED, data={
            'image': request.build_absolute_uri(master.avatar.url)
        })


class MgmtUpdatePortfolioStatusView(generics.GenericAPIView):
    view_name = 'mgmt-update-portfolio-status'
    serializer_class = Serializer
    permission_classes = (IsAdmin,)
    queryset = Master.objects.all()

    def get_object(self):
        master = super().get_object()
        portfolio_id = self.kwargs['portfolio_id']
        try:
            return master.portfolio.get(pk=portfolio_id)
        except PortfolioImage.DoesNotExist as ex:
            raise NotFound(f'Portfolio with id {portfolio_id} is not found')

    def patch(self, request, *args, **kwargs):
        """
        Sets a description for a portfolio image

        Input:

        ```
        {
          'status': 'ON_MODERATION/ACCEPTED'
        }
        ```

        Response:
        200 OK

        400 Bad Request
        """
        # TODO use serializer with choices
        portfolio_status = request.data.get('status', None)

        portfolio = self.get_object()
        portfolio.status = portfolio_status
        portfolio.save()

        return Response(status=status.HTTP_200_OK)
