from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from src.apps.core.exceptions import NoContentError
from src.apps.core.permissions import IsClient
from . import master_utils
from .filtering import FilteringFunctions, FilteringParams
from .models import Master
from .serializers import MasterSerializer


class MasterListView(generics.ListAPIView):
    view_name = 'master-list'

    permission_classes = (permissions.IsAuthenticated, IsClient)

    def get(self, request, **kwargs):
        """
        Returns a list of masters filtered by the following params.

        coordinates *required* - comma separated list of latitude and longitude values.
        stands for 'current' coordinates of the caller

        date_range - comma separated list of dates '2017-10-25,2017-10-26'.
        default range is two weeks from the current day

        time_range - comma separated list of times '10:30,11:30'.
        default range is '8:00,23:00'

        services - comma separated list of services.
        default list contains all services

        distance - maximum distance in km. default is 20km
        """
        params = FilteringParams(request)
        masters, slots = master_utils.search(params, FilteringFunctions.search)
        favorites, others = master_utils.split(masters, request.user.client)

        return Response(data={
            'favorites': master_utils.sort_and_serialize_masters(favorites, params, slots),
            'others': master_utils.sort_and_serialize_masters(others, params, slots)
        })


class MasterSearchView(generics.ListAPIView):
    view_name = 'master-search'

    queryset = Master.objects.all()

    permission_classes = (permissions.IsAuthenticated, IsClient)

    def get(self, request, **kwargs):
        """
        Returns a list of masters, who can do the selected service
        at the specific date and time, or if not specified, at any time
        in the following two weeks

        query params:

        service - *required*

        date - *optional* format: 2017-10-25

        time - *optional* format 11:30
        """
        params = FilteringParams(request)
        if params.date and params.time:
            masters, slots = master_utils.search(params, FilteringFunctions.datetime)
        else:
            masters, slots = master_utils.search(params, FilteringFunctions.anytime)

        favorites, others = master_utils.split(masters, request.user.client)

        return Response(data={
            'favorites': master_utils.sort_and_serialize_masters(favorites, params, slots),
            'others': master_utils.sort_and_serialize_masters(others, params, slots)
        })


class MasterBestMatchView(generics.ListAPIView):
    view_name = 'master-best-match'

    queryset = Master.objects.all()

    permission_classes = (permissions.IsAuthenticated, IsClient)

    def get(self, request, **kwargs):
        """
        Returns a single master, who can do the selected service
        at the specific date and time

        query params:

        date - *required*

        time - *required*

        service - *required*
        """
        params = FilteringParams(request)
        if params.date and params.time:
            masters, slots = master_utils.search(params, FilteringFunctions.datetime)
        else:
            raise ValidationError('please provide date, time and service params')

        if len(masters) == 0:
            raise NoContentError(detail='no masters found for query')

        favorites, regular = master_utils.split(masters, request.user.client)

        # I fucking love python magic
        masters = favorites or regular

        # getting the top guy
        best_match = master_utils.sort_masters(masters, params.coordinates,
                                               params.distance)[0]
        # serializing him
        output_data = master_utils.sort_and_serialize_masters([best_match], params, slots)

        return Response(data=output_data[0])


class MasterDetailView(generics.RetrieveAPIView):
    """
    Returns the detailed view of a master

    """
    view_name = 'master-detail'
    queryset = Master.objects.all()
    serializer_class = MasterSerializer
    permission_classes = (permissions.IsAuthenticated,)
