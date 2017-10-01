from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from src.apps.categories.models import Service
from src.apps.masters import time_slot_utils, master_utils
from . import filtering
from .models import Master
from .serializers import MasterSerializer, MasterListSerializer, TimeSlotSerializer


class MasterListView(generics.ListAPIView):
    view_name = 'master-list'

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, **kwargs):
        # TODO use drf serializer for validation
        params = filtering.prepare_filtering_params(request.query_params)
        result = filtering.search_for_masters(params)
        masters = master_utils.sort_masters(result, params['coordinates'], params['distance'])
        serializer = MasterListSerializer(masters, many=True, context={
            'coordinates': params['coordinates']
        })
        # TODO add favourites
        return Response(serializer.data)


class MasterSearchView(generics.ListAPIView):
    view_name = 'master-search'

    queryset = Master.objects.all()

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, **kwargs):
        # service_id, client_id, date(optional), time(optional)
        # TODO implement me, yo!
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


class MasterDetailView(generics.RetrieveAPIView):
    view_name = 'master-detail'
    queryset = Master.objects.all()
    serializer_class = MasterSerializer
    permission_classes = (permissions.IsAuthenticated,)


class MasterScheduleView(generics.RetrieveAPIView):
    view_name = 'master-schedule'
    queryset = Master.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, **kwargs):
        """
        Returns dates and time slots of a master when he can do the specified service
        """
        master = self.get_object()
        service_id = request.query_params.get('service')
        if not service_id:
            raise ValidationError("'service' parameter is not specified")
        try:
            service = Service.objects.get(pk=service_id)
        except Service.DoesNotExist as ex:
            raise ValidationError(f"Service with id={service_id} doesn't exist")
        else:
            result = []
            # TODO return only those who can make it to the current client
            for schedule in master.schedule.all():
                available_slots = time_slot_utils \
                    .find_available_starting_slots(service, schedule.time_slots.all())

                slots_json = TimeSlotSerializer(instance=available_slots,
                                                many=True).data
                # TODO unify date format
                if slots_json:
                    result.append({
                        'time_slots': slots_json,
                        'date': schedule.date.strftime('%Y-%m-%d')
                    })
            # TODO what if he can't make it at any time? return empty list or warning?
            return Response(data=result)
