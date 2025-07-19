from django.urls import path
from .views import IntegrationViewSet, RTIRViewSet, CerebrateViewSet, VirusTotalViewSet

urlpatterns = [
    path('', IntegrationViewSet.as_view({
        'get': 'list'
    })),
    path('rtir/', RTIRViewSet.as_view({
        'get': 'retrieve',
        'put': 'update'
    })),
    path('rtir/toggle/', RTIRViewSet.as_view({
        'post': 'toggle_status'
    })),
    path('cerebrate/', CerebrateViewSet.as_view({
        'get': 'retrieve',
        'put': 'update'
    })),
    path('cerebrate/toggle/', CerebrateViewSet.as_view({
        'post': 'toggle_status'
    })),
    path('cerebrate/refresh/', CerebrateViewSet.as_view({
        'post': 'refresh'
    })),
    path('vt/', VirusTotalViewSet.as_view({
        'get': 'retrieve',
        'put': 'update'
    })),
    path('vt/toggle/',VirusTotalViewSet.as_view({
        'post': 'toggle_status'
    })),
]
