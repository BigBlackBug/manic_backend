import heapq

from rest_framework import generics, filters, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .filters import MasterListFilter
from .models import Master
from .serializers import MasterSerializer, MasterListSerializer, MasterScheduleSerializer


class MasterComparable:
    def __init__(self, master, value):
        self.master = master
        self.value = value

    def __lt__(self, other):
        return self.value < other.value


class MasterListView(generics.ListAPIView):
    view_name = 'master-list'

    queryset = Master.objects.all()
    serializer_class = MasterListSerializer

    filter_class = MasterListFilter
    # date, time, service,  distance,
    filter_backends = (filters.DjangoFilterBackend,)

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        target_distance = request.query_params.get('distance')
        if target_distance:
            coordinates = request.query_params.get('coordinates')
            if not coordinates:
                raise ValidationError('Please specify \'coordinates\' query param')
            try:
                lat, lon = map(float, coordinates.split(','))
            except:
                raise ValidationError('\'coordinates\' query param is not valid. '
                                      'It should be a comma-separated tuple of two floats')
            data = self.filter_by_distance(queryset, float(target_distance), lat, lon)

            serializer_class = self.get_serializer_class()
            kwargs['context'] = self.get_serializer_context()
            kwargs['context']['coordinates'] = (lat, lon)

            serializer = serializer_class(data, many=True, **kwargs)
        else:
            data = queryset
            serializer = self.get_serializer(data, many=True)
        # TODO add favourites
        return Response(serializer.data)

    def filter_by_distance(self, queryset, target_distance: float, lat: float, lon: float):
        result = []
        for master in queryset:
            distance = master.distance(lat, lon)
            if distance < target_distance:
                heapq.heappush(result, MasterComparable(master, target_distance - distance))
        return [comp.master for comp in result]


class MasterDetailView(generics.RetrieveAPIView):
    view_name = 'master-detail'
    queryset = Master.objects.all()
    serializer_class = MasterSerializer
    permission_classes = (permissions.IsAuthenticated,)


class MasterScheduleView(generics.RetrieveAPIView):
    view_name = 'master-schedule'
    queryset = Master.objects.all()
    serializer_class = MasterScheduleSerializer
    permission_classes = (permissions.IsAuthenticated,)

