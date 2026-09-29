from rest_framework import serializers
from .models import Campus, Building, Floor, Room


class CampusSerializer(serializers.ModelSerializer):
    building_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Campus
        fields = ['id', 'name', 'code', 'description', 'sort_order', 'building_count']


class BuildingSerializer(serializers.ModelSerializer):
    campus_name = serializers.ReadOnlyField(source='campus.name')
    campus_code = serializers.ReadOnlyField(source='campus.code')

    class Meta:
        model = Building
        fields = ['id', 'name', 'code', 'campus', 'campus_name', 'campus_code']


class FloorSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True)
    campus_id = serializers.IntegerField(source='building.campus.id', read_only=True)
    campus_name = serializers.CharField(source='building.campus.name', read_only=True)

    class Meta:
        model = Floor
        fields = ['id', 'campus', 'building', 'building_name', 'campus_id', 'campus_name', 'floor_number']


class RoomSerializer(serializers.ModelSerializer):
    floor_name = serializers.SerializerMethodField()
    campus_name = serializers.SerializerMethodField()
    building_name = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'floor', 'floor_name', 'campus_name', 'building_name', 'name', 'sort', 'created_at', 'updated_at']

    def get_floor_name(self, obj):
        if obj.floor:
            return f'{obj.floor.floor_number}层'
        return ''

    def get_campus_name(self, obj):
        if obj.floor and obj.floor.building and obj.floor.building.campus:
            return obj.floor.building.campus.name
        return ''

    def get_building_name(self, obj):
        if obj.floor and obj.floor.building:
            return obj.floor.building.name
        return ''
