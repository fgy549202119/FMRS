from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EquipmentTypeViewSet, EquipmentViewSet, EquipmentTypeRequestViewSet
from location.views import CampusViewSet, BuildingViewSet, FloorViewSet

router = DefaultRouter()
router.register(r'types', EquipmentTypeViewSet)
router.register(r'type-requests', EquipmentTypeRequestViewSet, basename='type-request')
router.register(r'list', EquipmentViewSet)

compat_router = DefaultRouter()
compat_router.register(r'campus', CampusViewSet, basename='campus')
compat_router.register(r'buildings', BuildingViewSet, basename='building')
compat_router.register(r'floors', FloorViewSet, basename='floor')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(compat_router.urls)),
]
