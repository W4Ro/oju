from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from dateutil.relativedelta import relativedelta
from django.db.models import Count, F
from django.db.models.functions import TruncMonth, TruncDate
from django.utils import timezone
from .serializers import EntityStatisticsSerializer, PlatformStatisticsSerializer, AlertCategorySerializer, MostImpactedEntitiesSerializer, CaseByCategorySerializer, EntityAttackDataSerializer, RecentAlertSerializer, PlatformUrlScreenshotSerializer
from apps.alertes.models import Alert
from apps.entities.models import Entity, Platform
import datetime
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.roles.permissions import HasPermission

class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet for dashboard statistics and analytics.
    """
    permission_classes = [IsAuthenticated]
    http_method_names = ['get']

    def get_permissions(self):
        """Get required permissions based on action"""
        permission_map = {
            'entity_statistics': ['dashboard_view'],
            'platform_statistics': ['dashboard_view'],
            'alerts_by_category': ['dashboard_view'],
            'alerts_by_status':['dashboard_view'],
            'total': ['dashboard_view'],
            'alerts_timeline': ['dashboard_view'],
            'most_impacted_entities': ['dashboard_view', 'entities_view'],
            'cases_by_category': ['dashboard_view'],
            'entity_cases_by_category': ['dashboard_view', 'entities_view'],
            'recent_alerts': ['dashboard_view', 'entities_view', 'alerts_view'],
            'carousel':['dashboard_carousel_view', 'platforms_view'],
        }
        
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]
    
    @swagger_auto_schema(
        operation_description="Get daily alerts count timeline",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'dates': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        ),
                        'counts': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_INTEGER)
                        )
                    }
                )
            ),
            400: "Bad Request",
            500: "Internal Server Error"
        }
    )
    @action(detail=False, methods=['get'], url_path='alerts-timeline')
    def alerts_timeline(self, request):
        """
        Get daily alerts count since the beginning.
        """
        try:
            first_alert = Alert.objects.order_by('created_at').first()
            if not first_alert:
                return Response({
                    'dates': [],
                    'counts': []
                }, status=status.HTTP_200_OK)
            
            start_date = first_alert.created_at.date()
            end_date = timezone.now().date()
            
            daily_counts = Alert.objects.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            ).annotate(
                day=TruncDate('created_at')
            ).values('day').annotate(
                count=Count('id')
            ).order_by('day')
            
            current_date = start_date
            dates_list = []
            counts_list = []
            counts_dict = {entry['day']: entry['count'] for entry in daily_counts}
            
            while current_date <= end_date:
                dates_list.append(current_date.strftime('%Y-%m-%d'))
                counts_list.append(counts_dict.get(current_date, 0))
                current_date += timezone.timedelta(days=1)
            
            response_data = {
                'dates': dates_list,
                'counts': counts_list
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": "An error occurred processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Get today's alert statistics by status",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'labels': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="Alert status labels"
                        ),
                        'data': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_INTEGER),
                            description="Count for each alert status"
                        ),
                        'colors': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="Colors for each alert status"
                        )
                    }
                )
            ),
            400: "Bad Request",
            500: "Internal Server Error"
        }
    )
    @action(detail=False, methods=['get'], url_path='alerts-by-status')
    def alerts_by_status(self, request):
        """
        Get today's alert statistics by status.
        """
        try:
            status_mapping = {
                'new': {'label': 'New', 'color': '#FF0000', 'count': 0},
                'in_progress': {'label': 'In Progress', 'color': '#FFA500', 'count': 0},
                'resolved': {'label': 'Resolved', 'color': '#28A745', 'count': 0},
                'false_positive': {'label': 'False Positive', 'color': '#6C757D', 'count': 0},
            }

            today = timezone.now().date()
            today_start = datetime.datetime.combine(today, datetime.time.min, tzinfo=timezone.utc)
            today_end = datetime.datetime.combine(today, datetime.time.max, tzinfo=timezone.utc)

            alert_counts = Alert.objects.filter(
                created_at__gte=today_start,
                created_at__lte=today_end
            ).values('status').annotate(
                count=Count('id')
            ).order_by('status')

            for entry in alert_counts:
                if entry['status'] in status_mapping:
                    status_mapping[entry['status']]['count'] = entry['count']

            response_data = {
                'labels': [v['label'] for v in status_mapping.values()],
                'data': [v['count'] for v in status_mapping.values()],
                'colors': [v['color'] for v in status_mapping.values()]
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "An error occurred processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Get the list of URLs and screenshots of all active platforms",
        responses={
            200: openapi.Response(
                description="List of URLs and screenshots",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'url': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                format=openapi.FORMAT_URI,
                                description="Platform URL",
                                example="https://example.com"
                            ),
                            'screenshot_url': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="Platform screenshot URL",
                                format=openapi.FORMAT_URI,
                                nullable=True
                            )
                        }
                    )
                )
            ),
            500: "Server Error",
            400: "Bad Request"
        }
    )
    @action(detail=False, methods=['get'], url_path='urls-screenshots')
    def carousel(self, request):
        """
        Returns the list of URLs and screenshots of all active platforms.
        """
        try:
            platforms = Platform.objects.filter(is_active=True)
            serializer = PlatformUrlScreenshotSerializer(platforms, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Get monthly entity count statistics for the past 12 months",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'name': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the statistics series"),
                        'data': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'month': openapi.Schema(type=openapi.TYPE_STRING, description="Month name (abbreviated)"),
                                    'count': openapi.Schema(type=openapi.TYPE_INTEGER, description="Entity count for the month")
                                }
                            )
                        )
                    }
                )
            ),
            400: "Bad Request",
            500: "Internal Server Error"
        }
    )
    @action(detail=False, methods=['get'], url_path='entity-statistics')
    def entity_statistics(self, request):
        """
        Get entity count statistics per month for the last 12 months.
        """
        try:
            end_date = timezone.now()
            start_date = end_date - relativedelta(months=11)
            
            monthly_counts = Entity.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            ).annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month')
            
            month_mapping = {
                1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 
                7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
            }
            
            result_data = []
            current_month = start_date.month
            current_year = start_date.year
            
            for _ in range(12):
                month_name = month_mapping[current_month]
                result_data.append({
                    'month': month_name,
                    'count': 0
                })
                
                current_month += 1
                if current_month > 12:
                    current_month = 1
                    current_year += 1
            
            for entry in monthly_counts:
                month_index = (entry['month'].month - start_date.month) % 12
                result_data[month_index]['count'] = entry['count']
            
            response_data = {
                'name': 'Total Entities',
                'data': result_data
            }
            
            serializer = EntityStatisticsSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        operation_description="Get total number of entities and platforms",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_entities': openapi.Schema(type=openapi.TYPE_INTEGER, description="Total number of entities"),
                        'total_platforms': openapi.Schema(type=openapi.TYPE_INTEGER, description="Total number of platforms")
                    }
                )
            ),
            500: "Internal Server Error"
        }
    )
    @action(detail=False, methods=['get'], url_path='total')
    def total(self, request):
        """
        Get the total count of entities and platforms.
        """
        try:
            total_entities = Entity.objects.count()
            total_platforms = Platform.objects.count()

            return Response({
                'total_entities': total_entities,
                'total_platforms': total_platforms
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': "An error occured processing your request"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @swagger_auto_schema(
        operation_description="Get monthly platform count statistics for the past 12 months",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'name': openapi.Schema(type=openapi.TYPE_STRING, description="Name of the statistics series"),
                        'data': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'month': openapi.Schema(type=openapi.TYPE_STRING, description="Month name (abbreviated)"),
                                    'count': openapi.Schema(type=openapi.TYPE_INTEGER, description="Platform count for the month")
                                }
                            )
                        )
                    }
                )
            ),
            400: "Bad Request",
            500: "Internal Server Error"
        }
    )
    @action(detail=False, methods=['get'], url_path='platform-statistics')
    def platform_statistics(self, request):
        """
        Get platform count statistics per month for the last 12 months.
        """
        try:
            end_date = timezone.now()
            start_date = end_date - relativedelta(months=11)
            
            monthly_counts = Platform.objects.filter(
                created_at__gte=start_date,
                created_at__lte=end_date
            ).annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month')
            month_mapping = {
                1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 
                7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
            }
            
            result_data = []
            current_month = start_date.month
            current_year = start_date.year
            
            for _ in range(12):
                month_name = month_mapping[current_month]
                result_data.append({
                    'month': month_name,
                    'count': 0
                })
                
                current_month += 1
                if current_month > 12:
                    current_month = 1
                    current_year += 1
            
            for entry in monthly_counts:
                month_index = (entry['month'].month - start_date.month) % 12
                result_data[month_index]['count'] = entry['count']
            
            response_data = {
                'name': 'Total Sites',
                'data': result_data
            }
            
            serializer = PlatformStatisticsSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @swagger_auto_schema(
        operation_description="Get today's alerts statistics by category",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'labels': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="Category labels"
                        ),
                        'data': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_INTEGER),
                            description="Count for each category"
                        ),
                        'colors': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="Colors for each category"
                        )
                    }
                )
            ),
            400: "Bad Request",
            500: "Internal Server Error"
        }
    )
    @action(detail=False, methods=['get'], url_path='alerts-by-category')
    def alerts_by_category(self, request):
        """
        Get today's alerts statistics by category.
        """
        try:
            today = timezone.now().date()
            today_start = datetime.datetime.combine(today, datetime.time.min, tzinfo=timezone.utc)
            today_end = datetime.datetime.combine(today, datetime.time.max, tzinfo=timezone.utc)
            
            categories = {
                'ssl': {'label': 'SSL Problem', 'color': '#FF0000', 'count': 0},
                'ssl_expiredSoon': {'label': 'SSL Expires Soon', 'color': '#FFA500', 'count': 0},
                'domain_unvailable': {'label': 'Domain Issue', 'color': '#007BFF', 'count': 0},
                'domain_expiredSoon': {'label': 'Domain Expires Soon', 'color': '#17A2B8', 'count': 0},
                'defacement': {'label': 'Defacement', 'color': '#28A745', 'count': 0},
                'availability': {'label': 'Availability', 'color': '#6C757D', 'count': 0},
                'vt': {'label': 'Flaged on VirusTotal', 'color': '#6610f2', 'count': 0},
            }
            
            today_alerts = Alert.objects.filter(
                created_at__gte=today_start,
                created_at__lte=today_end
            )
            
            for alert in today_alerts:
                if alert.alert_type in categories:
                    categories[alert.alert_type]['count'] += 1
            
            response_data = {
                'labels': [cat_data['label'] for cat_type, cat_data in categories.items()],
                'data': [cat_data['count'] for cat_type, cat_data in categories.items()],
                'colors': [cat_data['color'] for cat_type, cat_data in categories.items()]
            }
            
            serializer = AlertCategorySerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Get the 10 most impacted entities by alerts with monthly breakdown",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'entities': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'data': openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(type=openapi.TYPE_INTEGER)
                                    )
                                }
                            )
                        ),
                        'categories': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        ),
                        'colors': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        )
                    }
                )
            ),
            400: "Bad Request",
            500: "Internal Server Error"
        }
    )
    @action(detail=False, methods=['get'], url_path='most-impacted-entities')
    def most_impacted_entities(self, request):
        """
        Get the 10 most impacted entities by alerts with monthly breakdown for the last 12 months.
        """
        try:
            end_date = timezone.now()
            start_date = end_date - relativedelta(months=11)
            
            month_mapping = {
                1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 
                7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
            }
            
            months_list = []
            current_month = start_date.month
            current_year = start_date.year
            
            for _ in range(12):
                months_list.append(month_mapping[current_month])
                current_month += 1
                if current_month > 12:
                    current_month = 1
                    current_year += 1
            
            top_entities = Entity.objects.filter(
                alerts__created_at__gte=start_date,
                alerts__created_at__lte=end_date
            ).annotate(
                alert_count=Count('alerts')
            ).order_by('-alert_count')[:10]
            
            colors = ["#605DFF", "#FE7A36", "#AD63F6", "#D71C00", "#00BFFF", "#32CD32", 
                    "#FF69B4", "#FFD700", "#8A2BE2", "#20B2AA"]
                    
            while len(colors) < len(top_entities):
                colors.extend(colors)
            colors = colors[:len(top_entities)]
            
            entities_data = []
            
            for entity in top_entities:
                monthly_counts = Alert.objects.filter(
                    entity=entity,
                    created_at__gte=start_date,
                    created_at__lte=end_date
                ).annotate(
                    month=TruncMonth('created_at')
                ).values('month').annotate(
                    count=Count('id')
                ).order_by('month')
                
                monthly_data = [0] * 12
                
                for entry in monthly_counts:
                    month_index = (entry['month'].month - start_date.month) % 12
                    monthly_data[month_index] = entry['count']
                
                entities_data.append({
                    'name': entity.name,
                    'data': monthly_data
                })
            
            response_data = {
                'entities': entities_data,
                'categories': months_list,
                'colors': colors
            }
            
            serializer = MostImpactedEntitiesSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

    @swagger_auto_schema(
        operation_description="Get cases by category statistics for all time",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'name': openapi.Schema(type=openapi.TYPE_STRING, description="Series name"),
                        'data': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_INTEGER),
                            description="Count for each category"
                        ),
                        'categories': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="Category names"
                        ),
                        'colors': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="Colors for each category"
                        )
                    }
                )
            ),
            400: "Bad Request",
            500: "Internal Server Error"
        }
    )
    @action(detail=False, methods=['get'], url_path='cases-by-category')
    def cases_by_category(self, request):
        """
        Get the total number of cases by category for all time.
        """
        try:
            categories = {
                'ssl': {
                    'display': 'SSL Problem',
                    'color': '#FF5733',
                    'count': 0
                },
                'ssl_expiredSoon': {
                    'display': 'SSL Expires',
                    'color': '#33FF57',
                    'count': 0
                },
                'domain_unvailable': {
                    'display': 'Domain Issue',
                    'color': '#3357FF',
                    'count': 0
                },
                'domain_expiredSoon': {
                    'display': 'Domain Expires',
                    'color': '#FF33A8',
                    'count': 0
                },
                'defacement': {
                    'display': 'Defacement',
                    'color': '#FFD733',
                    'count': 0
                },
                'availability': {
                    'display': 'Availability',
                    'color': '#A833FF',
                    'count': 0
                },
                'vt': {
                    'display': 'Flagged on VirusTotal',
                    'color': '#33FFF5',
                    'count': 0
                }
            }
            
            alert_counts = Alert.objects.values('alert_type').annotate(
                count=Count('id')
            ).order_by('alert_type')
            
            for entry in alert_counts:
                if entry['alert_type'] in categories:
                    categories[entry['alert_type']]['count'] = entry['count']
            
            display_names = [cat_data['display'] for _, cat_data in categories.items()]
            counts = [cat_data['count'] for _, cat_data in categories.items()]
            colors = [cat_data['color'] for _, cat_data in categories.items()]
            
            response_data = {
                'name': 'Cas Totaux',
                'data': counts,
                'categories': display_names,
                'colors': colors
            }
            
            serializer = CaseByCategorySerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Get case statistics by category for each entity",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'entities': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additionalProperties=openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'value': openapi.Schema(type=openapi.TYPE_INTEGER),
                                        'name': openapi.Schema(type=openapi.TYPE_STRING)
                                    }
                                )
                            )
                        )
                    }
                )
            ),
            400: "Bad Request",
            500: "Internal Server Error"
        }
    )
    @action(detail=False, methods=['get'], url_path='entity-cases-by-category')
    def entity_cases_by_category(self, request):
        """
        Get case statistics by category for each entity.
        """
        try:
            entities_with_alerts = Entity.objects.filter(
                alerts__isnull=False
            ).distinct()
            
            entities_data = {}
            
            for entity in entities_with_alerts:
                alert_counts = Alert.objects.filter(
                    entity=entity
                ).values('alert_type').annotate(
                    count=Count('id')
                ).order_by('-count')
                
                alert_type_mapping = {
                    'ssl': 'SSL Problem',
                    'ssl_expiredSoon': 'SSL Certificate Expires Soon',
                    'domain_unvailable': 'Domain Unavailable',
                    'domain_expiredSoon': 'Domain Expires Soon',
                    'defacement': 'Defacement',
                    'availability': 'Availability Issue',
                    'other': 'Other',
                    'vt': 'Flagged on VirusTotal'
                }
                
                entity_data = []
                for alert in alert_counts:
                    alert_name = alert_type_mapping.get(alert['alert_type'], alert['alert_type'])
                    entity_data.append({
                        'value': alert['count'],
                        'name': alert_name
                    })
                
                if entity_data:
                    entities_data[entity.name] = entity_data
            
            response_data = {
                'entities': entities_data
            }
            
            serializer = EntityAttackDataSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

    @swagger_auto_schema(
        operation_description="Get the 10 most recent alerts",
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_STRING),
                            'url': openapi.Schema(type=openapi.TYPE_STRING),
                            'case': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'created_at': openapi.Schema(type=openapi.TYPE_STRING),
                            'focal': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    )
                )
            ),
            400: "Bad Request",
            500: "Internal Server Error"
        }
    )
    @action(detail=False, methods=['get'], url_path='recent-alerts')
    def recent_alerts(self, request):
        """
        Get the 10 most recent alerts with related entity and platform information.
        """
        try:
            recent_alerts = Alert.objects.select_related(
                'entity', 'platform'
            ).order_by('-created_at')[:10]
            
            result = []
            
            for alert in recent_alerts:
                result.append({
                    'id': alert.id,  
                    'url': alert.platform.url,
                    'type': alert.get_alert_type_display(),
                    'created_at': alert.created_at,
                    'entity': alert.entity.name
                })
            
            serializer = RecentAlertSerializer(result, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )