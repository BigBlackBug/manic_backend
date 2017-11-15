import datetime
import logging

from rest_framework import generics, permissions, parsers, status, mixins
from rest_framework.exceptions import ValidationError, NotFound, \
    PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from src.apps.core.exceptions import NoContentError
from src.apps.core.permissions import IsClient, IsMaster
from src.apps.core.serializers import ImageListSerializer, \
    DescriptionImageSerializer
from src.apps.masters import time_slot_utils
from src.apps.masters.permissions import IsMasterIDCorrect
from . import master_utils
from .filtering import FilteringFunctions, FilteringParams
from .models import Master, PortfolioImage, Schedule
from .serializers import MasterSerializer, CreateScheduleSerializer, \
    MasterCreateSerializer

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
        params = FilteringParams(request)
        masters, slots = master_utils.search(params, FilteringFunctions.search)
        favorites, others = master_utils.split(masters,
                                               request.user.is_client() and
                                               request.user.client)

        return Response(data={
            'favorites': master_utils.sort_and_serialize_masters(
                favorites, params, slots),
            'others': master_utils.sort_and_serialize_masters(
                others, params, slots)
        })

    def post(self, request, *args, **kwargs):
        if request.user.has_account():
            raise PermissionDenied(
                detail='This phone already has an associated account')
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
          'available_slots':[{
            'date':'2018-10-20',
            'time_slots':['10:30', '15:00']
          }]
        }
        ```
        """
        params = FilteringParams(request)
        if params.date and params.time:
            masters, slots = master_utils.search(
                params, FilteringFunctions.datetime)
        else:
            masters, slots = master_utils.search(
                params, FilteringFunctions.anytime)

        favorites, others = master_utils.split(masters, request.user.client)

        return Response(data={
            'favorites': master_utils.sort_and_serialize_masters(
                favorites, params, slots),
            'others': master_utils.sort_and_serialize_masters(
                others, params, slots)
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

        Response:
        200 OK

        Json with the **Master** model. See `/masters` endpoint for description

        """
        params = FilteringParams(request)
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
            [best_match], params, slots)

        return Response(data=output_data[0])


class MasterDetailView(generics.RetrieveAPIView):
    view_name = 'master-detail'
    queryset = Master.objects.all()
    serializer_class = MasterSerializer
    permission_classes = (permissions.IsAuthenticated,)

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
          'status': 'ON_REVIEW/VERIFIED',
          'about': 'I am super cool',
          'avatar':'url-to-avatar',
          'services':[{service model}],
          'location': {'lat':10, 'lon':12},
          'schedule':[{schedule model}]
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
        """
        return super().get(request, *args, **kwargs)


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
        {'image-file-name':'portfolio-id',...}
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
        ids = {}
        for image in images:
            portfolio_image = PortfolioImage.objects.create(master=master,
                                                            image=image)
            ids[image.name] = portfolio_image.id
        master.save()

        return Response(status=status.HTTP_201_CREATED, data=ids)


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
          'description': 'hey, look!'
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
            image.save()

        return Response(status=status.HTTP_200_OK)


class CreateDeleteScheduleView(mixins.DestroyModelMixin,
                               mixins.CreateModelMixin,
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

    def delete(self, request, *args, **kwargs):
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
