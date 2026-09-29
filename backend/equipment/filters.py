import django_filters
from .models import Equipment


class EquipmentFilter(django_filters.FilterSet):
    sequence_number = django_filters.NumberFilter(field_name='sequence_number')
    sequence_number_from = django_filters.NumberFilter(field_name='sequence_number', lookup_expr='gte')
    sequence_number_to = django_filters.NumberFilter(field_name='sequence_number', lookup_expr='lte')

    class Meta:
        model = Equipment
        fields = ['equipment_type', 'status', 'sequence_number']
