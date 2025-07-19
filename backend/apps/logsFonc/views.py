from django.shortcuts import render
from .serializers import SystemLogSerializer
from .models import SystemLog
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as django_filters
from django.http import HttpResponse
import csv
import xlsxwriter
from io import BytesIO
from django.db.models import Q
from datetime import datetime
from apps.roles.permissions import HasPermission
from apps.mail_setting.models import EmailLog
from apps.mail_setting.serializers import EmailLogSerializer
from apps.logsFonc.utils import create_system_log
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone

import logging
logger = logging.getLogger(__name__)


class EmailLogFilter(django_filters.FilterSet):
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    sent_after = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    sent_before = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    recipient = django_filters.CharFilter(method='filter_recipient')
    
    class Meta:
        model = EmailLog
        fields = {
            'subject': ['icontains'],
            'status': ['exact', 'in'],
            'is_html': ['exact'],
        }
        
    def filter_recipient(self, queryset, name, value):
        return queryset.filter(
            Q(to_recipients__contains=[value]) |
            Q(cc_recipients__contains=[value]) |
            Q(bcc_recipients__contains=[value])
        )


class EmailLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EmailLog.objects.all()
    serializer_class = EmailLogSerializer
    filterset_class = EmailLogFilter
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['subject', 'to_recipients', 'cc_recipients', 'bcc_recipients']
    ordering_fields = ['created_at', 'sent_at', 'subject', 'status']
    ordering = ['-created_at']
    http_method_names = ['get']

    def get_permissions(self):
        permission_map = {
            'list': 'logs_view',
        }
        
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]

    @swagger_auto_schema(
        operation_description="Retrieve the list of sent emails with filtering possibility",
        manual_parameters=[
            openapi.Parameter(
                'created_after',
                openapi.IN_QUERY,
                description="Filter emails created after this date (format: YYYY-MM-DD HH:MM)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME,
            ),
            openapi.Parameter(
                'created_before',
                openapi.IN_QUERY,
                description="Filter emails created before this date (format: YYYY-MM-DD HH:MM)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME,
            ),
            openapi.Parameter(
                'sent_after',
                openapi.IN_QUERY,
                description="Filter emails sent after this date (format: YYYY-MM-DD HH:MM)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME,
            ),
            openapi.Parameter(
                'sent_before',
                openapi.IN_QUERY,
                description="Filter emails sent before this date (format: YYYY-MM-DD HH:MM)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME,
            ),
            openapi.Parameter(
                'subject',
                openapi.IN_QUERY,
                description="Search in topic (case insensitive)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'recipient',
                openapi.IN_QUERY,
                description="Search for a recipient in to, cc or bcc",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Filter by status",
                type=openapi.TYPE_STRING,
                enum=[choice[0] for choice in EmailLog.EmailStatus.choices],
            ),
        ],
        responses={
            200: EmailLogSerializer(many=True),
            400: "Invalid filter settings"
        },
        tags=["EmailLog"]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class SystemLogFilter(django_filters.FilterSet):
    start_date = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte'
    )
    end_date = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte'
    )
    name = django_filters.CharFilter(
        field_name='user__username',
        lookup_expr='icontains'
    )
    details = django_filters.CharFilter(
        method='filter_details'
    )

    def filter_details(self, queryset, name, value):
        return queryset.filter(details__icontains=value)

    class Meta:
        model = SystemLog
        fields = ['start_date', 'end_date', 'name', 'details']

class SystemLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SystemLog.objects.all()
    serializer_class = SystemLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [django_filters.DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = SystemLogFilter
    ordering_fields = ['created_at', 'user__username']
    ordering = ['-created_at']


    def get_permissions(self):
        permission_map = {
            'list': 'logs_view',
            'export': 'logs_export',
        }
        
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(details__icontains=search)
            )
        
        return queryset

    @swagger_auto_schema(
        operation_summary="List of system logs",
        operation_description="Returns the list of system logs with filtering capability",
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search in name and details",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'name',
                openapi.IN_QUERY,
                description="Filter by name",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'details',
                openapi.IN_QUERY,
                description="Filter by details",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'start_date',
                openapi.IN_QUERY,
                description="Start date (format: YYYY-MM-DD HH:MM:SS)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'end_date',
                openapi.IN_QUERY,
                description="End date (format: YYYY-MM-DD HH:MM:SS)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                description="Filter by date (created_at) ou nom (name)",
                type=openapi.TYPE_STRING,
                required=False
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    @swagger_auto_schema(
        operation_summary="Export system logs",
        operation_description="export system logs in csv or xlsx format",
        manual_parameters=[
            openapi.Parameter(
                'export_format',
                openapi.IN_QUERY,
                description="Export format (csv or xlsx)",
                type=openapi.TYPE_STRING,
                required=True,
                enum=['csv', 'xlsx']
            ),
        ]
    )
    def export(self, request):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            format = request.query_params.get('export_format', '')
            
            filename = f"system_logs_{timezone.now().strftime('%Y%m%d_%H%M%S')}"

            if format == 'csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
                
                writer = csv.writer(response)
                writer.writerow(['Date', 'Username', 'Details'])
                
                for log in queryset:
                    writer.writerow([
                        log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        log.user.username,
                        str(log.details) if log.details else ''
                    ])
                
                return response
                
            elif format == 'xlsx':
                output = BytesIO()
                workbook = xlsxwriter.Workbook(output)
                worksheet = workbook.add_worksheet()
                
                
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#F0F0F0'
                })
                
                
                headers = ['Date', 'Username', 'Details']
                for col, header in enumerate(headers):
                    worksheet.write(0, col, header, header_format)
                
            
                for row, log in enumerate(queryset, start=1):
                    worksheet.write(row, 0, log.created_at.strftime('%Y-%m-%d %H:%M:%S'))
                    worksheet.write(row, 1, log.user.username)
                    worksheet.write(row, 2, str(log.details) if log.details else '')
                
                workbook.close()
                output.seek(0)
                
                response = HttpResponse(
                    output.read(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename={filename}".xlsx"'
                return response
            
            return Response(
                {"error": "Unsupported format. Use 'csv' or 'xlsx'"},
                status=400
            )
        except Exception as e:
            return Response(
                {"error": "Unexpected error has occured"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )