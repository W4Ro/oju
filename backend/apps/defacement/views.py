from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as django_filters
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from apps.roles.permissions import HasPermission
from apps.logsFonc.utils import create_system_log

from .models import Defacement
from .serializers import DefacementDetailSerializer, DefacementListSerializer
from django.shortcuts import get_object_or_404
from core.common_function import *

class DefacementFilter(django_filters.FilterSet):
    date_after = django_filters.DateTimeFilter(field_name='date', lookup_expr='gte')
    date_before = django_filters.DateTimeFilter(field_name='date', lookup_expr='lte')
    entity_name = django_filters.CharFilter(field_name='entity__name', lookup_expr='icontains')
    platform_url = django_filters.CharFilter(field_name='platform__url', lookup_expr='icontains')
    
    class Meta:
        model = Defacement
        fields = {
            'is_defaced': ['exact'],
            'entity': ['exact'],
            'platform': ['exact'],
        }

class DefacementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Defacement.objects.select_related('entity', 'platform').all()
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DefacementFilter
    search_fields = ['entity__name', 'platform__url', 'details']
    ordering_fields = ['date', 'entity__name', 'platform__url']
    ordering = ['-date']

    def get_permissions(self):
        """Get required permissions based on action"""
        permission_map = {
            'list': ['defacement_view', 'entities_view'],
            'retrieve': ['defacement_view', 'entities_view'],
            'reset_state':['defacement_reset', 'entities_view'],
        }
        
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DefacementDetailSerializer
        return DefacementListSerializer
    
    @swagger_auto_schema(
        operation_summary="List all defacements",
        operation_description="Returns the list of defacements with filtering capability",
        manual_parameters=[
            openapi.Parameter(
                'date_after',
                openapi.IN_QUERY,
                description="Filter after this date (format: YYYY-MM-DD HH:MM)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME,
                required=False,
            ),
            openapi.Parameter(
                'date_before',
                openapi.IN_QUERY,
                description="Filtrer after this date (format: YYYY-MM-DD HH:MM)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME,
                required=False,
            ),
            openapi.Parameter(
                'entity_name',
                openapi.IN_QUERY,
                description="Filter by entity name (partial search)",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                'platform_url',
                openapi.IN_QUERY,
                description="Filter by platform URL (partial search)",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                'is_defaced',
                openapi.IN_QUERY,
                description="Filter by defacement status",
                type=openapi.TYPE_BOOLEAN,
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Details of a defacement",
        operation_description="Returns the full details of a specific defacement",
        responses={
            200: DefacementDetailSerializer,
            404: "Plateform not found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Reset to normal state",
        operation_description="Resets a platform's normal state to its current state",
        request_body=None,
        responses={
            200: "Status reset successfully",
            404: "Platform not found"
        }
    )
    @action(detail=True, methods=['post'])
    def reset_state(self, request, pk=None):
        try:
            defacement = self.get_object()
            if not defacement.is_defaced:
                return Response(
                    {"error": "This platform is not currently marked as defaced"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if defacement.last_state and defacement.last_state_tree:
                defacement.normal_state = defacement.last_state
                defacement.normal_state_tree = defacement.last_state_tree
                defacement.last_state = {}
                defacement.last_state_tree = ''
                defacement.is_defaced = False
                defacement.details = ''
                defacement.date = timezone.now()
                defacement.save()
                create_system_log(assign_user(request.user), f"reset defacement value of {defacement.platform.url}")
            return Response({
                "message": "Normal state reset successfully",
                "platform": defacement.platform.url
            })
        except:
            return Response(
                {"error": "An unexpected error har occured"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )