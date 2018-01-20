import datetime
import logging

from rest_framework import generics, permissions, parsers, status, mixins
from rest_framework.exceptions import ValidationError, NotFound, \
    PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.apps.core.exceptions import NoContentError
from src.apps.core.permissions import IsClient, IsMaster
from src.apps.core.serializers import ImageListSerializer, \
    DescriptionImageSerializer, ImageSerializer
from src.apps.masters import time_slot_utils
from src.apps.masters.permissions import IsMasterIDCorrect
from . import master_utils
from .filtering import FilteringFunctions, FilteringParams
from .models import Master, PortfolioImage, Schedule, MasterStatus
from .serializers import MasterSerializer, CreateScheduleSerializer, \
    MasterCreateSerializer, CreateFeedbackSerializer, MasterUpdateSerializer

logger = logging.getLogger(__name__)


class MasterListCreateView(generics.ListCreateAPIView):
    view_name = 'master-list-create'
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (parsers.MultiPartParser, parsers.JSONParser)
    # not used. required by swagger
    serializer_class = MasterSerializer

    def get(self, request, **kwargs):
        """
        Returns a list of masters filtered by the following params

        `coordinates` **required** - comma separated list of
        latitude and longitude values. stands for 'current'
        coordinates of the caller

        `date_range` - comma separated list of dates '2017-10-25,2017-10-26'.
        default range is two weeks from the current day

        `time_range` - comma separated list of times '10:30,11:30'.
        default range is '8:00,23:00'

        `services` - comma separated list of services.
        default list contains all services

        `distance` - maximum distance in km. default is 20km

        The output is also sorted according to the rating of the master
        and distance to the `coordinates`

        Response:
        200 OK
        ```
        {
          //each element of the array is an instance of **Master**
          'favorites:':[]
          'others':[]
        }
        ```
        **Master** model

        ```
        {
          'id':100500,
          'first_name':'Maria'
          'about': 'I am super cool',
          'avatar':'url-to-avatar',
          'services':[{service model}],
          'location': {'lat':10, 'lon':12},
          'distance':10.5
        }

        ```

        400 Bad Request
        """
        params = FilteringParams(request.query_params, request=request)
        masters, slots = master_utils.search(params, FilteringFunctions.search)
        favorites, others = master_utils.split(masters,
                                               request.user.is_client(
                                                   request) and
                                               request.user.client)

        return Response(data={
            'favorites': master_utils.sort_and_serialize_masters(
                request, favorites, params, slots),
            'others': master_utils.sort_and_serialize_masters(
                request, others, params, slots)
        })

    def post(self, request, *args, **kwargs):
        """
        Creates a master.

        Note that it is a multi-part POST request.

        Input:
        ```
        {
          'id': 100500,
          'first_name': 'Maria',
          'gender': 'F/M',
          'date_of_birth': '1988-10-29',
          'about': 'I am god',
          'avatar':'multi-part-image',
          'email':'super@cool.com',
          'services':'1,2,3',
        }
        ```

        Response:
        201 Created

        403 Forbidden - If an account is already associated with this phone

        400 Bad Request
        """
        if not request.user.is_master(request):
            raise PermissionDenied(
                detail='A user must be a Master to access this endpoint')

        if not request.user.master.status == MasterStatus.DUMMY:
            raise PermissionDenied(detail=f'Unable to initialize master '
                                          f'with id {request.user.master.id}')

        serializer = MasterCreateSerializer(
            data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class MasterSearchView(generics.ListAPIView):
    view_name = 'master-search'

    queryset = Master.objects.all()

    permission_classes = (permissions.IsAuthenticated, IsClient)

    def get(self, request, **kwargs):
        """
        Returns masters who can do the selected service
        at the specific date and time, or if not specified, at any time
        in the following two weeks

        Query params:

        `service` - **required** a service id

        `coordinates` **required** - comma separated list of
        latitude and longitude values. stands for 'current'
        coordinates of the caller

        `date` - format: 2017-10-25

        `time` - format 11:30

        Response:
        200 OK
        ```
        {
          //each element of the array is an instance of **Master**
          'favorites:':[]
          'others':[]
        }
        ```
        **Master** model

        ```
        {
          'id':100500,
          'first_name':'Maria'
          'about': 'I am super cool',
          'avatar':'url-to-avatar',
          'services':[{service model}],
          'location': {'lat':10, 'lon':12},
          'distance':10.5,
          // dates and times when the desired service may be done
          'available_slots':[{
            'date':'2018-10-20',
            'time_slots':['10:30', '15:00']
          }]
        }
        ```
        """
        params = FilteringParams(request.query_params, request=request)
        if params.date and params.time:
            masters, slots = master_utils.search(
                params, FilteringFunctions.datetime)
        else:
            masters, slots = master_utils.search(
                params, FilteringFunctions.anytime)

        favorites, others = master_utils.split(masters, request.user.client)

        return Response(data={
            'favorites': master_utils.sort_and_serialize_masters(
                request, favorites, params, slots),
            'others': master_utils.sort_and_serialize_masters(
                request, others, params, slots)
        })


class MasterBestMatchView(generics.ListAPIView):
    view_name = 'master-best-match'

    queryset = Master.objects.all()

    permission_classes = (permissions.IsAuthenticated, IsClient)

    def get(self, request, **kwargs):
        """
        Returns a single master, who can do the selected service
        at the specific date and time

        Query params:

        `service` **required** - A service id

        `date` **required** format: 2017-10-25

        `time` **required** format 11:30

        `coordinates` **required** - comma separated list of
        latitude and longitude values. stands for 'current'
        coordinates of the caller

        Response:
        200 OK - Json with the **Master** model.
        See `/masters` endpoint for description

        204 No content

        """
        params = FilteringParams(request.query_params, request=request)
        if params.date and params.time:
            masters, slots = master_utils.search(
                params, FilteringFunctions.datetime)
        else:
            raise ValidationError(
                'please provide date, time and service params')

        if len(masters) == 0:
            raise NoContentError(detail='no masters found for query')

        favorites, regular = master_utils.split(masters, request.user.client)

        # I fucking love python magic
        masters = favorites or regular

        # getting the top guy
        best_match = master_utils.sort_masters(masters, params.coordinates,
                                               params.distance)[0]
        # serializing him
        output_data = master_utils.sort_and_serialize_masters(
            request, [best_match], params, slots)

        return Response(data=output_data[0])


class MasterDetailUpdateView(mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin,
                             generics.GenericAPIView):
    view_name = 'master-detail-update'
    queryset = Master.objects.all()
    get_permission_classes = (permissions.IsAuthenticated,)
    patch_permission_classes = (permissions.IsAuthenticated, IsMasterIDCorrect)

    def get(self, request: Request, *args, **kwargs):
        """
        Returns the detailed view of a master

        Response:
        200 OK
        ```
        {
          'id':100500,
          'first_name':'Maria'
          'phone':'88005553535',
          'email':'supercool@master.com',
          'status': 'ON_REVIEW/DELETED/BLOCKED/VERIFIED',
          'about': 'I am super cool',
          'avatar':'url-to-avatar',
          'services':[{service model}],
          'location': {'lat':10, 'lon':12},
          //only upcoming schedules are returned
          'schedule':[{schedule model}],
          'feedback':[{feedback model}],
          'balance':{
            'future':10,
            'on_hold':0,
            'transferred':1000,
            'debt':2000,
          },
          'portfolio':[{
            'id': 100,
            'url': 'image-url',
            'description': 'did this in 10 minutes, yo',
            'status': 'ON_MODERATION/ACCEPTED',
          },...]
          'rating':4.3,
          'gender':'F'
          'date_of_birth':'1980-10-20'
        }

        ```

        **Schedule**
        ```
        {
          'date':'2017-10-20',
          'time_slots:[{
            'time':'10:30',
            'taken':False
          }]
        }
        ```
        **Feedback**
        ```
        {
          'rating':4.0,
          'text':'hey',
          'date':'2017-11-20',
          'client':{
            'id':1,
            'avatar':'link-to-img',
            'first_name':'John'
          }
        }
        ```
        """
        return super().retrieve(request, *args, **kwargs)

    def get_serializer_class(self):
        if not self.request:
            # TODO this is a fucking bug of the schema generation module
            return MasterSerializer

        if self.request.method == 'PATCH':
            return MasterUpdateSerializer
        return MasterSerializer

    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [permission() for permission in
                    self.patch_permission_classes]
        return [permission() for permission in self.get_permission_classes]

    def patch(self, request, *args, **kwargs):
        """
        Updates a master

        All fields are optional.

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
        }

        ```

        Responses:

        200 OK

        400 Bad Request
        """
        return super().partial_update(request, *args, **kwargs)


class MasterAvatarUpdateView(APIView):
    view_name = 'master-avatar-update'

    parser_classes = (parsers.MultiPartParser,)
    permission_classes = (IsAuthenticated, IsMasterIDCorrect)

    def patch(self, request, **kwargs):
        """
        Adds or replaces the avatar of the master

        Input:

        multi-part form data where `image` field contains the image

        Response:
        201 Created `{'image':'url-to-the-image'}`

        400 Bad Request
        """
        master = request.user.master
        logger.info(f'Updating an avatar for '
                    f'master {master.first_name}, '
                    f'id={master.id}')

        serializer = ImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image = serializer.validated_data['image']
        master.avatar = image
        master.save()

        return Response(status=status.HTTP_201_CREATED, data={
            'image': request.build_absolute_uri(master.avatar.url)
        })


class MeMasterView(generics.RetrieveAPIView):
    view_name = 'me-master'
    permission_classes = (IsAuthenticated, IsMaster)
    serializer_class = MasterSerializer

    def get_object(self):
        return self.request.user.master

    def get(self, request, *args, **kwargs):
        """
        Returns a representation of current logged-in master.

        Response:
        200 OK

        See **/masters/<id>** endpoint for output json format
        """
        return super().get(request, *args, **kwargs)


class AddPortfolioItemsView(generics.GenericAPIView):
    view_name = 'add-portfolio-items'
    serializer_class = ImageListSerializer
    parser_classes = (parsers.MultiPartParser,)
    permission_classes = (IsAuthenticated, IsMasterIDCorrect)

    def post(self, request, **kwargs):
        """
        Adds a portfolio item to a master

        Input:

        multi-part form data where `images` field contains a list of images

        Response:
        201 Created
        ```
        [{'id':10,'image':'url-to-image'},...]
        ```

        400 Bad Request
        """
        master = request.user.master
        logger.info(f'Adding portfolio images for'
                    f'master {master.first_name}, '
                    f'id={master.id}')

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        images = serializer.validated_data['images']
        data = []
        for image in images:
            portfolio_image = PortfolioImage.objects.create(master=master,
                                                            image=image)
            data.append({
                'id': portfolio_image.id,
                'url': request.build_absolute_uri(portfolio_image.image.url)
            })
        master.save()

        return Response(status=status.HTTP_201_CREATED, data=data)


class DeletePortfolioItemView(generics.DestroyAPIView):
    view_name = 'delete-portfolio-item'
    serializer_class = ImageSerializer
    permission_classes = (IsAuthenticated, IsMasterIDCorrect)

    def get_object(self):
        portfolio_id = self.kwargs['portfolio_id']
        master = self.request.user.master
        try:
            return master.portfolio.get(pk=portfolio_id)
        except PortfolioImage.DoesNotExist as ex:
            raise NotFound(f'Portfolio with id {portfolio_id} is not found')

    def delete(self, request, *args, **kwargs):
        """
        Removes a portfolio item from a master

        Response:
        204 No Content

        400 Bad Request
        """
        return super().delete(request, *args, **kwargs)


class AddPortfolioItemDescriptionView(generics.GenericAPIView):
    view_name = 'add-portfolio-item-description'
    serializer_class = DescriptionImageSerializer
    permission_classes = (IsAuthenticated, IsMasterIDCorrect)

    def patch(self, request, *args, **kwargs):
        """
        Sets a description for a portfolio image

        Input:

        ```
        [{
          'image_id': 100500,
          'description': 'hey, look!',
          'status': 'ON_MODERATION/ACCEPTED'
        }]
        ```

        Response:
        200 OK

        400 Bad Request
        """
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        for item in data:
            image = PortfolioImage.objects.get(pk=item['image_id'])
            image.description = item['description']
            if 'status' in item:
                image.status = item.get('status')
            image.save()

        return Response(status=status.HTTP_200_OK)


class CreateDeleteScheduleView(mixins.CreateModelMixin,
                               mixins.UpdateModelMixin,
                               generics.GenericAPIView):
    view_name = 'create-delete-schedule'
    serializer_class = CreateScheduleSerializer
    queryset = Master.objects.all()
    permission_classes = (IsAuthenticated, IsMasterIDCorrect)

    def post(self, request, *args, **kwargs):
        """
        Creates or updates a schedule at the specified date.

        Parses the `time_slots` string and creates all new empty
        TimeSlots for the schedule at `date`

        ```
        [{
          'date': '2017-10-10',
          'time_slots': '10:00-13:30,15:00,17:00-19:00'
        }]
        ```
        Response:
        200 OK
        """
        return super().create(request, *args, **kwargs)

    # TODO WARNING. TEMPORARY STUB.
    # All because our lovely Android dev is too lazy
    # to adapt to a proper endpoint, instead he chose to stick with this
    def patch(self, request, *args, **kwargs):
        """
        Deletes time slots of schedule at `date`

        ```
        [{
          'date': '2017-10-10',
          'time_slots': '10:00-13:30,15:00,17:00-19:00'
        }]
        ```
        Response:

        200 OK
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        date = serializer.validated_data['date']
        slot_string = serializer.validated_data['time_slots']

        time_tuples = time_slot_utils.parse_time_slots(slot_string,
                                                       include_last=True)

        try:
            schedule = request.user.master.schedule.get(date=date)
        except Schedule.DoesNotExist:
            raise NotFound(detail=f'Schedule at {date} was not found')
        else:
            for time_tuple in time_tuples:
                schedule.delete_slot(datetime.
                                     time(hour=time_tuple.hour,
                                          minute=time_tuple.minute))
            if len(schedule.time_slots.all()) == 0:
                schedule.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class AddFeedbackView(generics.CreateAPIView):
    view_name = 'add-feedback'
    serializer_class = CreateFeedbackSerializer
    queryset = Master.objects.all()
    permission_classes = (IsAuthenticated, IsClient,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request:
            # TODO this is a fucking bug of the schema generation module
            context.update({
                'master': self.get_object()
            })
        return context

    def post(self, request, *args, **kwargs):
        """
        Leaves a feedback to a master

        ```
        {
          'rating': 3.0,
          'text': 'good enough',
          'date': '2017-10-10'
        }
        ```
        Response:

        200 OK

        403 Forbidden - If you are trying to leave feedback to a master
        someone who hasn't served you yet
        """
        client = request.user.client
        master = self.get_object()
        if master.times_served(client) == 0:
            raise PermissionDenied(
                detail='You may not leave feedback '
                       'to masters who did not serve you')

        return super().post(request, *args, **kwargs)
