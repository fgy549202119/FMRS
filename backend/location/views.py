from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters
from django.db.models import Count
from backend.authentication import get_request_identity
from .models import Campus, Building, Floor, Room
from .serializers import CampusSerializer, BuildingSerializer, FloorSerializer, RoomSerializer


class CampusViewSet(viewsets.ModelViewSet):
    queryset = Campus.objects.annotate(building_count=Count('buildings')).order_by('sort_order', 'id')
    serializer_class = CampusSerializer

    @action(detail=False, methods=['get'])
    def options(self, request):
        data = list(Campus.objects.values('id', 'name', 'code'))
        return Response(data)


class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.select_related('campus').all()
    serializer_class = BuildingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['campus']

    @action(detail=False, methods=['get'], url_path='list_all')
    def list_all(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FloorViewSet(viewsets.ModelViewSet):
    queryset = Floor.objects.select_related('building', 'campus').all()
    serializer_class = FloorSerializer
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter]
    filterset_fields = ['building', 'campus']
    search_fields = ['floor_number']

    @action(detail=False, methods=['get'], url_path='by_building/(?P<building_id>[^/.]+)')
    def by_building(self, request, building_id=None):
        floors = self.get_queryset().filter(building_id=building_id)
        serializer = self.get_serializer(floors, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='batch_create')
    def batch_create(self, request):
        building_id = request.data.get('building')
        start_floor = request.data.get('start_floor', 1)
        end_floor = request.data.get('end_floor', 1)

        if not building_id:
            return Response({'code': 400, 'message': '请选择楼栋'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            building = Building.objects.select_related('campus').get(id=building_id)
        except Building.DoesNotExist:
            return Response({'code': 400, 'message': '楼栋不存在'}, status=status.HTTP_400_BAD_REQUEST)

        start_floor, end_floor = int(start_floor), int(end_floor)
        if start_floor > end_floor:
            start_floor, end_floor = end_floor, start_floor

        created = []
        for floor_num in range(start_floor, end_floor + 1):
            floor, created_flag = Floor.objects.get_or_create(
                campus=building.campus,
                building=building,
                floor_number=floor_num
            )
            if created_flag:
                created.append(floor)

        return Response({
            'code': 200,
            'message': f'成功创建 {len(created)} 个楼层（已存在的跳过）',
            'data': FloorSerializer(created, many=True).data
        })

    @action(detail=False, methods=['get'], url_path='list_all')
    def list_all(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.select_related('floor', 'floor__building', 'floor__building__campus').all()
    serializer_class = RoomSerializer
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter]
    filterset_fields = ['floor']
    search_fields = ['name']

    def get_queryset(self):
        qs = super().get_queryset()
        campus_id = self.request.query_params.get('campus_id')
        building_id = self.request.query_params.get('building_id')
        floor_id = self.request.query_params.get('floor_id')
        if floor_id:
            qs = qs.filter(floor_id=floor_id)
        elif building_id:
            qs = qs.filter(floor__building_id=building_id)
        elif campus_id:
            qs = qs.filter(floor__building__campus_id=campus_id)
        return qs

    @action(detail=False, methods=['post'], url_path='batch_create')
    def batch_create(self, request):
        floor_id = request.data.get('floor')
        start_num = request.data.get('start_num')
        end_num = request.data.get('end_num')
        name_prefix = request.data.get('name_prefix', '')
        name_suffix = request.data.get('name_suffix', '')

        if not floor_id:
            return Response({'code': 400, 'message': '请选择楼层'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            floor = Floor.objects.select_related('building', 'building__campus').get(id=floor_id)
        except Floor.DoesNotExist:
            return Response({'code': 400, 'message': '楼层不存在'}, status=status.HTTP_400_BAD_REQUEST)

        if start_num is None or end_num is None:
            return Response({'code': 400, 'message': '请输入起始号和结束号'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_num, end_num = int(start_num), int(end_num)
        except (ValueError, TypeError):
            return Response({'code': 400, 'message': '起始号和结束号必须为整数'}, status=status.HTTP_400_BAD_REQUEST)

        if start_num > end_num:
            start_num, end_num = end_num, start_num

        if end_num - start_num > 200:
            return Response({'code': 400, 'message': '单次批量创建不能超过200个房间'}, status=status.HTTP_400_BAD_REQUEST)

        created = []
        skipped = 0
        for num in range(start_num, end_num + 1):
            room_name = f'{name_prefix}{num}{name_suffix}'
            room, created_flag = Room.objects.get_or_create(
                floor=floor,
                name=room_name,
                defaults={'sort': num}
            )
            if created_flag:
                created.append(room)
            else:
                skipped += 1

        msg_parts = []
        if created:
            msg_parts.append(f'成功创建 {len(created)} 个房间')
        if skipped:
            msg_parts.append(f'跳过 {skipped} 个已存在房间')
        message = '，'.join(msg_parts) if msg_parts else '没有新房间被创建'

        return Response({
            'code': 200,
            'message': message,
            'data': RoomSerializer(created, many=True).data
        })
