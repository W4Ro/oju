from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Entity, Platform
from .serializers import EntitySerializer, PlatformSerializer, EntityAlertStatsSerializer
from core.common_function import *
from apps.roles.permissions import HasPermission
from apps.roles.models import RolePermission
import json
from rest_framework.exceptions import ValidationError

from apps.logsFonc.utils import create_system_log
from apps.focal_points.serializers import FocalPointSerializer
from apps.alertes.models import Alert


class EntityViewSet(viewsets.ModelViewSet):
    """
        ViewSet for entity management.
        Allows all CRUD operations on entities.
    """
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_user_permissions(self, user):
        """Retrieve user permissions"""
        try:
            return list(RolePermission.objects.filter(
                role_id=user.role_id
            ).values_list('permission__permission_code', flat=True))
        except:
            return []
    
    def get_permissions(self):
        """Get required permissions based on action"""
        permission_map = {
            'list': 'entities_view',
            'retrieve': 'entities_view',
            'create': 'entities_create',
            'focal_points': ['focal_points_view', 'entities_view'],
            'update': 'entities_edit',
            'destroy': 'entities_delete',
            'alerts_by_status': 'entities_view',
            'status_details': 'entities_view',
            'alerts_by_type': 'entities_view',
        }
        
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]

    @swagger_auto_schema(
        operation_summary="List of entities",
        operation_description="Returns the list of entities with filtering capability",
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search in name and description", type=openapi.TYPE_STRING),
            openapi.Parameter('has_platforms', openapi.IN_QUERY, description="Filter entities with platforms", type=openapi.TYPE_BOOLEAN),
        ],
        responses={
            200: openapi.Response(
                description="List of entities",
                schema=EntitySerializer(many=True)
            ),
            401: "Not authenticated"
        },
        tags=["Entities"]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        search = request.query_params.get('search', '')
        has_platforms = request.query_params.get('has_platforms')

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        if has_platforms is not None:
            if has_platforms.lower() == 'true':
                queryset = queryset.filter(platforms__isnull=False).distinct()
            elif has_platforms.lower() == 'false':
                queryset = queryset.filter(platforms__isnull=True)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Details of an entity",
        operation_description="Returns details of a specific entity",
        responses={
            200: EntitySerializer,
            404: "Entity not found",
            401: "Not authenticated"
        },
        tags=["Entities"]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get entity focal points",
        operation_description="Returns the list of focal points associated with this entity",
        responses={
            200: FocalPointSerializer(many=True),
            404: "Entity not found",
            401: "Not authenticated"
        },
        tags=["Entities"]
    )
    @action(detail=True, methods=['get'])
    def focal_points(self, request, pk=None):
        """Get all focal points for a specific entity"""
        try:
            entity = self.get_object()
            focal_points = entity.focal_points.all()
            serializer = FocalPointSerializer(focal_points, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Create entity",
        operation_description="Create new entity",
        request_body=EntitySerializer,
        responses={
            201: EntitySerializer,
            400: "Invalid data",
            401: "Not authenticated"
        },
        tags=['Entities']
    )
    def create(self, request, *args, **kwargs):
        try:
            error, data = assignment_check({
                'name', 'description', 'focal_points_ids'
            }, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not isinstance(data["focal_points_ids"], list):
                return Response(
                    {"error": "focal_points_ids must be list of UUIDs"}
                )
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            create_system_log(assign_user(request.user), f"Create new entity {data['name']}")
            
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response(
                {"error": str_exception(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @swagger_auto_schema(
        operation_summary="Entity update",
        operation_description="Update entity",
        request_body=EntitySerializer,
        responses={
            200: EntitySerializer,
            400: "Invalid data",
            404: "Entity not found",
            401: "Not authenticated"
        },
        tags=['Entities']
    )
    def update(self, request, *args, **kwargs):
        try:
            error, data = assignment_check({
                'name', 'description', 'focal_points_ids'
            }, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not isinstance(data["focal_points_ids"], list):
                return Response(
                    {"error": "focal_points_ids must be list of UUIDs"}
                )
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            create_system_log(assign_user(request.user), f"Update entities {instance.id}")
            
            return Response(serializer.data)
        
        except ValidationError as e:
            return Response(
                {"error": str_exception(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Delete entity",
        operation_description="Deletes an entity and all its associated platforms",
        responses={
            204: "Deletion successful",
            404: "Entity not fond",
            401: "Not authenticated"
        },
        tags=["Entities"]
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)

            create_system_log(assign_user(request.user), f"Delete entities {instance.id}")
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Get alerts by status",
        operation_description="Returns the number of alerts by status for this entity",
        responses={
            200: "Dictionary with alert statuses and counts",
            404: "Entity not found",
            401: "Not authenticated"
        },
        tags=["Entities"]
    )
    @action(detail=True, methods=['get'])
    def alerts_by_status(self, request, pk=None):
        """Get alerts by status for a specific entity"""
        try:
            entity = self.get_object()
            from django.db.models import Count
            
            alerts_by_status = entity.alerts.values('status').annotate(
                count=Count('id')
            ).order_by('status')
            
            result = {status[1]: 0 for status in Alert.STATUS_CHOICES}
            
            for item in alerts_by_status:
                status_code = item['status']
                status_name = dict(Alert.STATUS_CHOICES).get(status_code, status_code)
                result[status_name] = item['count']
            
            return Response(result)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
    @swagger_auto_schema(
        operation_summary="Get alert status details",
        operation_description="Returns the total number of alerts, open alerts, and closed alerts for this entity",
        responses={
            200: "Dictionary with alert status counts",
            404: "Entity not found",
            401: "Not authenticated"
        },
        tags=["Entities"]
    )
    @action(detail=True, methods=['get'])
    def status_details(self, request, pk=None):
        """Get alert status details for a specific entity"""
        try:
            entity = self.get_object()
            from django.db.models import Count, Q
            from datetime import datetime, timedelta
            
            today = datetime.now()
            start_of_month = datetime(today.year, today.month, 1)

            total_alerts = entity.alerts.count()
            
            open_alerts = entity.alerts.filter(
                status__in=['new', 'in_progress']
            ).count()
            
            closed_alerts = entity.alerts.filter(
                status__in=['resolved', 'false_positive']
            ).count()
            
            alerts_this_month = entity.alerts.filter(
                created_at__gte=start_of_month
            ).count()
            
            resolved_this_month = entity.alerts.filter(
                status__in=['resolved', 'false_positive'],
                updated_at__gte=start_of_month
            ).count()
            
            previous_month = start_of_month - timedelta(days=1)
            previous_month_start = datetime(previous_month.year, previous_month.month, 1)
            
            alerts_previous_month = entity.alerts.filter(
                created_at__gte=previous_month_start,
                created_at__lt=start_of_month
            ).count()
            
            saved_percentage = 0
            if alerts_previous_month > 0:
                change = ((alerts_this_month - alerts_previous_month) / alerts_previous_month) * 100
                saved_percentage = -change  
            
            open_percentage = 0
            if alerts_this_month > 0:
                open_percentage = (entity.alerts.filter(
                    status__in=['new', 'in_progress'],
                    created_at__gte=start_of_month
                ).count() / alerts_this_month) * 100
            
            worked_percentage = 0
            previous_month_resolved = entity.alerts.filter(
                status__in=['resolved', 'false_positive'],
                updated_at__gte=previous_month_start,
                updated_at__lt=start_of_month
            ).count()
            
            if previous_month_resolved > 0:
                worked_percentage = ((resolved_this_month - previous_month_resolved) / previous_month_resolved) * 100
            
            result = {
                'total_alerts': total_alerts,
                'open_alerts': open_alerts,
                'closed_alerts': closed_alerts,
                'stats': {
                    'saved_this_month': alerts_this_month,
                    'saved_this_month_percentage': round(saved_percentage, 2),
                    'open_this_month': entity.alerts.filter(
                        status__in=['new', 'in_progress'],
                        created_at__gte=start_of_month
                    ).count(),
                    'open_this_month_percentage': round(open_percentage, 2),
                    'worked_on_this_month': resolved_this_month,
                    'worked_on_this_month_percentage': round(worked_percentage, 2)
                }
            }
        
            
            return Response(result)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_summary="Get alerts by type",
        operation_description="Returns the number of alerts by type for this entity",
        responses={
            200: "Dictionary with alert types and counts",
            404: "Entity not found",
            401: "Not authenticated"
        },
        tags=["Entities"]
    )
    @action(detail=True, methods=['get'])
    def alerts_by_type(self, request, pk=None):
        """Get alerts by type for a specific entity"""
        try:
            entity = self.get_object()
            from django.db.models import Count

            alerts_by_type = entity.alerts.values('alert_type').annotate(
                count=Count('id')
            ).order_by('alert_type')
            
            result = {alert_type[1]: 0 for alert_type in Alert.ALERT_TYPES}
            
            
            for item in alerts_by_type:
                alert_type = item['alert_type']
                alert_type_name = dict(Alert.ALERT_TYPES).get(alert_type, alert_type)
                result[alert_type_name] = item['count']
            
            return Response(result)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PlatformViewSet(viewsets.ModelViewSet):
    """
        ViewSet for platform management.
        Allows all CRUD operations on platforms.
    """
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_user_permissions(self, user):
        """Retrieve user permissions"""
        try:
            return list(RolePermission.objects.filter(
                role_id=user.role_id
            ).values_list('permission__permission_code', flat=True))
        except:
            return []
        
    def get_permissions(self):
        """Get required permissions based on action"""
        permission_map = {
            'list': 'platforms_view',
            'retrieve': 'platforms_view',
            'create': 'platforms_create',
            'update': 'platforms_edit',
            'destroy': 'platforms_delete',
            'toggle_status': 'platforms_toggle',
            'serve_screenshot': 'platforms_view'
        }
        
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]


    @swagger_auto_schema(
        operation_description="Récupère et sert l'image de screenshot d'une plateforme spécifique",
        responses={
            200: "Image au format PNG",
            404: "Screenshot non trouvé",
            401: "Non authentifié",
            500: "Erreur interne du serveur"
        },
        tags=["Platforms"]
    )
    @action(detail=False, methods=['get'], url_path='screenshots/(?P<platform_id>.*)')
    def serve_screenshot(self, request, platform_id=None):
        """
        Récupère et sert l'image de screenshot d'une plateforme spécifique.
        """
        try:
            from django.conf import settings
            from django.http import HttpResponse
            import os, re, uuid

            if not platform_id:
                return Response(
                    {"error": "Platform ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            if not platform_id.endswith('.png'):
                return Response(
                    {"error": "Invalid format, must end with .png"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            uuid_str = platform_id[:-4]  
            
            try:
                uuid_obj = uuid.UUID(uuid_str)
            except ValueError:
                return Response(
                    {"error": "Platform not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            platform_exists = Platform.objects.filter(id=uuid_str).exists()
            if not platform_exists:
                return Response(
                    {"error": "Platform not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            screenshots_dir = os.path.abspath(os.path.join(settings.MEDIA_ROOT, 'screenshots'))
            screenshot_path = os.path.abspath(os.path.join(screenshots_dir, platform_id))
            
            if not screenshot_path.startswith(screenshots_dir):
                return Response(
                    {"error": "Invalid path"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not os.path.exists(screenshot_path) or not os.path.isfile(screenshot_path):
                return Response(
                    {"error": "Screenshot image not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            try:
                with open(screenshot_path, 'rb') as f:
                    image_data = f.read()
            except (IOError, PermissionError):
                return Response(
                    {"error": "Unable to read screenshot file"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            response = HttpResponse(image_data, content_type='image/png')
            response['Cache-Control'] = 'max-age=300' 
            response['Content-Disposition'] = f'inline; filename="{platform_id}"'
            return response
            
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    @swagger_auto_schema(
        operation_summary="List of platforms",
        operation_description="Returns the list of platforms with filtering capability",
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search URL", type=openapi.TYPE_STRING),
            openapi.Parameter('entity_id', openapi.IN_QUERY, description="Filter by Entity ID", type=openapi.TYPE_STRING, format='uuid'),
            openapi.Parameter('is_active', openapi.IN_QUERY, description="Filter by activation status", type=openapi.TYPE_BOOLEAN),
        ],
        responses={
            200: openapi.Response(description="List of plateforms", schema=PlatformSerializer(many=True)),
            401: "Not authenticated"
        },
        tags=["Platforms"]
    )
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            search = request.query_params.get('search', '')
            entity_id = request.query_params.get('entity_id')
            is_active = request.query_params.get('is_active')

            if search:
                queryset = queryset.filter(
                    Q(url__icontains=search)
                )

            if entity_id:
                queryset = queryset.filter(entity_id=entity_id)

            if is_active is not None:
                queryset = queryset.filter(is_active=is_active.lower() == 'true')

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Platform details",
        operation_description="Returns details of a specific platform",
        responses={
            200: PlatformSerializer,
            404: "Plateform not found",
            401: "Not authenticated"
        },
        tags=["Platforms"]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a platform",
        operation_description="Create a new platform",
        request_body=PlatformSerializer,
        responses={
            201: PlatformSerializer,
            400: "Data invalid",
            401: "Not authenticated"
        },
        tags=["Platforms"]
    )
    def create(self, request, *args, **kwargs):
        try:
            error, data = assignment_check({
                 'url', 'entity', 'is_active'
            }, request.data.items())
            if error:
                return Response(
                    {'error': data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            create_system_log(assign_user(request.user), f"Create another platform {data['url']}")
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        except ValidationError as e:
            return Response(
                {"error": str_exception(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Complete platform update",
        operation_description="Updates all fields of a platform",
        request_body=PlatformSerializer,
        responses={
            200: PlatformSerializer,
            400: "Data invalid",
            404: "Plateform not found",
            401: "Not authenticated"
        },
        tags=["Platforms"]
    )
    def update(self, request, *args, **kwargs):
        try:
            error, data = assignment_check({'url', 'is_active','entity'}, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            instance = self.get_object()
            
            serializer = self.get_serializer(instance, data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            create_system_log(assign_user(request.user), f"Update platform {instance.id}")
            
            return Response(serializer.data)
        
        except ValidationError as e:
            return Response(
                {"error": str_exception(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @swagger_auto_schema(
        operation_summary="Delete platform",
        responses={
            204: "Delete successfull",
            404: "Plateform not found",
            401: "Not authenticated"
        },
        tags=["Platforms"]
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            create_system_log(assign_user(request.user), f"Delete platform {instance.url}")
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="toggle status",
        operation_description="Enables or disables a platform",
        responses={
            200: PlatformSerializer,
            404: "Plateform not found",
            401: "Not authenticated"
        },
        tags=["Platforms"]
    )
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        try:
            platform = self.get_object()
            platform.is_active = not platform.is_active
            platform.save()
            serializer = self.get_serializer(platform)
            create_system_log(assign_user(request.user), f"Change plateform status: {platform.id}")
            
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class EntityAlertStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for entity alert statistics."""
    
    serializer_class = EntityAlertStatsSerializer
    http_method_names = ['get']

    def get_permissions(self):
        """Get required permissions based on action"""
        permission_map = {
            'retrieve': 'entities_view',
        }
        
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]
    
    def get_queryset(self):
        from django.db.models import Count, Q
        
        queryset = Entity.objects.annotate(
            total_alerts=Count('alerts'),
            open_alerts=Count('alerts', filter=Q(alerts__status__in=['new', 'in_progress'])),
            closed_alerts=Count('alerts', filter=Q(alerts__status__in=['resolved', 'false_positive']))
        )
        
        return queryset
    
    @swagger_auto_schema(
        operation_summary="Entity alert statistics details",
        operation_description="Returns alert statistics for a specific entity",
        responses={
            200: EntityAlertStatsSerializer,
            404: "Entity not found",
            401: "Not authenticated"
        },
        tags=["Entities"]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)