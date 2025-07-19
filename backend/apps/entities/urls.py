from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import EntityViewSet, PlatformViewSet, EntityAlertStatsViewSet

router = DefaultRouter()
router.register(r'platforms', PlatformViewSet)
router.register(r'', EntityViewSet)


urlpatterns = [
    path('alert-stats/<str:pk>/', EntityAlertStatsViewSet.as_view({
        'get': 'retrieve'
    }), name='entity-alert-stats-detail'),
    path('', include(router.urls)),
]