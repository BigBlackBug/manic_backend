from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from src.apps.categories.models import Service
from src.apps.core.exceptions import NoContentError
from src.apps.core.permissions import IsClient
from . import time_slot_utils, master_utils, gmaps_utils, utils
from .filtering import FilteringFunctions, FilteringParams
from .models import Master
from .serializers import MasterSerializer, SimpleMasterSerializer, TimeSlotSerializer


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
        result = master_utils.search(params, FilteringFunctions.search)
        favorites, masters = master_utils.split(result, request.user.client)

        return Response(data={
            'favorites': master_utils.sort_and_serialize_masters(favorites, params),
            'others': master_utils.sort_and_serialize_masters(masters, params)
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

        date - *optional*
        time - *optional*
        """
        params = FilteringParams(request)
        if params.date and params.time:
            result = master_utils.search(params, FilteringFunctions.datetime)
        else:
            result = master_utils.search(params, FilteringFunctions.anytime)

        favorites, masters = master_utils.split(result, request.user.client)

        return Response(data={
            'favorites': master_utils.sort_and_serialize_masters(favorites, params),
            'others': master_utils.sort_and_serialize_masters(masters, params)
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
            masters = master_utils.search(params, FilteringFunctions.datetime)
        else:
            raise ValidationError('please provide date, time and service params')

        if len(masters) == 0:
            raise NoContentError(detail='no masters found for query')

        favorites, regular = master_utils.split(masters, request.user.client)

        # I fucking love python magic
        masters = favorites or regular

        best_match = master_utils.sort_masters(masters, params.coordinates,
                                               params.distance)[0]
        serializer = SimpleMasterSerializer(best_match, context={
            'coordinates': params.coordinates
        })
        return Response(serializer.data)


class MasterDetailView(generics.RetrieveAPIView):
    # TODO docs
    view_name = 'master-detail'
    queryset = Master.objects.all()
    serializer_class = MasterSerializer
    permission_classes = (permissions.IsAuthenticated,)


# TODO remove this view, merge business logic with search-view
class MasterScheduleView(generics.RetrieveAPIView):
    view_name = 'master-schedule'
    queryset = Master.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsClient)

    def get(self, request, **kwargs):
        """
        Returns dates and time slots of a master when he can do the specified service,
        considering the current client's address
        query_params:

        service <int> *required*

        Schedule is limited to the following two weeks
        """
        master = self.get_object()
        params = FilteringParams(request, coords_required=False)
        service = params.service
        if not service:
            raise ValidationError("'service' parameter is not specified")
        try:
            service = Service.objects.get(pk=service)
        except Service.DoesNotExist as ex:
            raise ValidationError(f"Service with id={service} doesn't exist")
        else:
            result = []
            dates = utils.get_default_date_range()

            for schedule in master.schedule.filter(date__gte=dates[0], date__lte=dates[1]):
                available_slots = time_slot_utils \
                    .find_available_starting_slots(service, schedule.time_slots.all())
                good_slots = []
                for slot in available_slots:
                    # проверяем может ли мастер доехать от предыдушего заказа
                    location = request.user.client.address.location
                    if gmaps_utils.can_reach(schedule, location, slot.value):
                        good_slots.append(slot)

                slots_json = TimeSlotSerializer(instance=good_slots, many=True).data
                # TODO unify date format
                if slots_json:
                    result.append({
                        'time_slots': slots_json,
                        'date': schedule.date.strftime('%Y-%m-%d')
                    })
            return Response(data=result)
