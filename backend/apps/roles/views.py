from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count
from rest_framework.exceptions import ValidationError
from .models import Role, Permission
from .serializers import (
    RoleSerializer, 
    PermissionSerializer, 
    RoleDetailSerializer
)
from .permissions import HasPermission
from .services import RolePermissionCache
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.logsFonc.utils import create_system_log
from core.common_function import *
from core.common_function import *

cache_service = RolePermissionCache()


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    lookup_field = 'id'
    http_method_names = ['get']

    def get_permissions(self):
        permission_map = {
            'list': 'roles_view',
            'retrieve': 'roles_view',
        }
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]

    @swagger_auto_schema(
        operation_description="List all permissions",
        responses={
            200: PermissionSerializer(many=True)
        },
        tags=['Permissions']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a permission",
        responses={
            200: PermissionSerializer,
            404: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        },
        tags=['Permissions']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)



class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    lookup_field = 'id'
    http_method_names = ['get', 'post', 'put', 'delete']
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return RoleDetailSerializer
        return RoleSerializer

    def get_queryset(self):
        queryset = Role.objects.annotate(
            total_permissions=Count('role_permissions')
        )
        return queryset

    def get_permissions(self):
        permission_map = {
            'list': 'roles_view',
            'retrieve': 'roles_view',
            'create': 'roles_create',
            'update': 'roles_edit',
            'destroy': 'roles_delete',
            'search': 'roles_view',
            'toggle_status': 'roles_toggle',
        }
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]

    @swagger_auto_schema(
        operation_description="List all roles",
        responses={
            200: RoleSerializer(many=True)
        },
        tags=['Roles']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve a role",
        responses={
            200: RoleSerializer(many=True),
            404: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        },
        tags=['Roles']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new role",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'permissions': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING, format='uuid')
                )
            }
        ),
        responses={
            201: RoleSerializer,
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        },
        tags=['Roles']
    )
    def create(self, request, *args, **kwargs):
        try:
            error, data = assignment_check({'name', 'description', 'permissions', 'is_active'}, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            permissions = data.get('permissions', [])
            data['permissions_to_update'] = permissions
            if not isinstance(permissions, list):
                return Response(
                    {"error": "permissions must be a list"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if permissions:
                existing_permissions = set(Permission.objects.filter(
                    id__in=permissions).values_list('id', flat=True))
                invalid_permissions = set(str(p) for p in permissions) - set(str(p) for p in existing_permissions)
                
                if invalid_permissions:
                    return Response(
                        {
                            "error": f"Invalid permission IDs {list(invalid_permissions)}",
                        },
                        status=status.HTTP_400_BAD_REQUESTs
                    )
            
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            role = serializer.save()

            create_system_log(assign_user(request.user), f"Created new role: {data['name']}")
            
            return Response(self.get_serializer(role).data, status=status.HTTP_201_CREATED)
        
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
        operation_description="Update a role",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'permissions': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID))
            }
        ),
        responses={
            200: RoleSerializer,
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        },
        tags=['Roles']
    )
    def update(self, request, *args, **kwargs):
        try:
            error, data = assignment_check({'name', 'description', 'permissions', 'is_active'}, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            permissions = data.get('permissions', [])
            data['permissions_to_update'] = permissions
            if not isinstance(permissions, list):
                return Response(
                    {"error": "permissions must be a list"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if permissions:
                existing_permissions = set(Permission.objects.filter(
                    id__in=permissions).values_list('id', flat=True))
                invalid_permissions = set(str(p) for p in permissions) - set(str(p) for p in existing_permissions)
                
                if invalid_permissions:
                    return Response(
                        {
                            "error": f"Invalid permission IDs {list(invalid_permissions)}",
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            instance = self.get_object()
            if instance.name == "Super Admin":
                return Response(
                    {"error": "Cannot edit the Super Admin role"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
           
            cache_service.invalidate_role_cache(instance.id)
            create_system_log(assign_user(request.user), f"Updated role: {instance.name}")
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
        operation_description="Delete a role",
        responses={
            204: "Successfully deleted",
            404: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        },
        tags=['Roles']
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.name == "Super Admin":
                return Response(
                    {"error": "Cannot delete the Super Admin role"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            self.perform_destroy(instance)
            create_system_log(assign_user(request.user), f"Deleted role: {instance.name}")
            
            cache_service.invalidate_role_cache(instance.id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Search roles",
        manual_parameters=[
            openapi.Parameter(
                'query',
                openapi.IN_QUERY,
                description="Search query (name or description)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: RoleSerializer(many=True),
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        },
        tags=['Roles']
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        try:
            query = request.query_params.get('query', '')
            if not query:
                return Response(
                    {"error": "Search query is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            roles = Role.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )
            serializer = self.get_serializer(roles, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Toggle role active status",
        request_body=None,
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            400: "Bad request",
            404: "Not found"
        },
        tags=["Roles"]
    )
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, id=None):
        """Toggle role active status"""
        try:
            role = self.get_object()
            if role.name == "Super Admin":
                return Response(
                    {"error": "Cannot toggle the Super Admin role"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            role.is_active = not role.is_active
            role.updated_at = timezone.now()
            role.save()
            create_system_log(assign_user(request.user), f"toggle role status: {role.name}")
            cache_service.invalidate_role_cache(role.id)
            
            return Response({"success": True, "is_active": role.is_active}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )