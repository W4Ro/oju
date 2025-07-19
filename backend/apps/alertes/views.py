from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters import rest_framework as django_filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from core.common_function import *
from .models import Alert
from .serializers import AlertSerializer
from apps.roles.permissions import HasPermission
from apps.logsFonc.utils import create_system_log

class AlertFilter(django_filters.FilterSet):
    date_after = django_filters.DateTimeFilter(field_name='date', lookup_expr='gte')
    date_before = django_filters.DateTimeFilter(field_name='date', lookup_expr='lte')
    entity_name = django_filters.CharFilter(field_name='entity__name', lookup_expr='icontains')
    platform_url = django_filters.CharFilter(field_name='platform__url', lookup_expr='icontains')
    
    class Meta:
        model = Alert
        fields = {
            'entity': ['exact'],
            'platform': ['exact'],
            'alert_type': ['exact', 'in'],
            'status': ['exact', 'in'],
            'details': ['icontains'],
        }

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    filterset_class = AlertFilter
    filter_backends = [django_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    http_method_names = ['get', 'put']
    search_fields = ['entity__name', 'platform__url', 'details']
    ordering_fields = ['date', 'updated_at', 'entity__name', 'platform__url']
    ordering = ['-date']
    
    def get_permissions(self):
        """Get required permissions based on action"""
        permission_map = {
            'list': ['alerts_view', 'entities_view'],
            'retrieve': ['alerts_view', 'entities_view'],
            'update': ['alerts_manage', 'entities_view']
        }
        
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]

    @swagger_auto_schema(
        operation_description="Retrieve the list of alerts with filtering possibility",
        manual_parameters=[
            openapi.Parameter(
                'date_after',
                openapi.IN_QUERY,
                description="Filter alerts after this date (format: YYYY-MM-DD HH:MM)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME,
            ),
            openapi.Parameter(
                'date_before',
                openapi.IN_QUERY,
                description="Filter alerts before this date (format: YYYY-MM-DD HH:MM)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME,
            ),
            openapi.Parameter(
                'entity_name',
                openapi.IN_QUERY,
                description="Filter by Entity name",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'platform_url',
                openapi.IN_QUERY,
                description="Filter by Platform URL",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'alert_type',
                openapi.IN_QUERY,
                description="Filter by alert type",
                type=openapi.TYPE_STRING,
                enum=[choice[0] for choice in Alert.ALERT_TYPES],
            ),
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Filter by status",
                type=openapi.TYPE_STRING,
                enum=[choice[0] for choice in Alert.STATUS_CHOICES],
            ),
            openapi.Parameter(
                'details',
                openapi.IN_QUERY,
                description="Search in details (case insensitive)",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: AlertSerializer(many=True),
            400: "Invalid filter settings"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


    @swagger_auto_schema(
        operation_description="Retrieve the details of a specific alert",
        responses={
            200: AlertSerializer,
            404: "Alert not found"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update the status of an alert",
        operation_description="Only allows you to change the status of an existing alert",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['status'],
            properties={
                'status': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=[choice[0] for choice in Alert.STATUS_CHOICES],
                    description="New alert status"
                )
            }
        ),
        responses={
            200: AlertSerializer,
            400: "Invalid request - Only the status can be edited",
            404: "Alerte not found",
            500: "Server Error"
        }
    )
    def update(self, request, *args, **kwargs):
        try:
            error, data = assignment_check({'status'}, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if set(request.data.keys()) - {'status'}:
                return Response(
                    {"error": "Only the 'status' field can be edited"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            instance = self.get_object()
            old_status = instance.status
            if old_status == data["status"]:
                return Response(
                    {"error": "Changed status first"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            response = super().update(request, *args, **kwargs)

            if response.status_code == 200:
                create_system_log(
                    assign_user(request.user),
                    f"Alert {instance.id} ({instance.get_alert_type_display()}) for entity '{instance.entity.name}' on platform '{instance.platform.url}' status changed from {old_status} to {data['status']}"
                )
            return response
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )