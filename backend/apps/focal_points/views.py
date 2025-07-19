from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from .models import FocalFunction, FocalPoint
from rest_framework.exceptions import ValidationError
from .serializers import (
    FocalFunctionSerializer,
    FocalPointSerializer,
    FocalPointListSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.common_function import *
from apps.roles.permissions import HasPermission
from apps.logsFonc.utils import create_system_log



class FocalFunctionViewSet(viewsets.ModelViewSet):
    queryset = FocalFunction.objects.all()
    serializer_class = FocalFunctionSerializer
    lookup_field = 'id'
    http_method_names = ["get", "put", "post", "delete"]

    def get_permissions(self):
        permission_map = {
            'list': 'focal_functions_view',
            'retrieve': 'focal_functions_view',
            'create': 'focal_functions_create',
            'update': 'focal_functions_edit',
            'destroy': 'focal_functions_delete'
        }
        
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]
    
    @swagger_auto_schema(
        operation_description="List all focal functions",
        request_body=None,
        responses={
            200: FocalFunctionSerializer(many=True)
        },
        tags=['Focal Point functions']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a focal function",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            201: openapi.Response(
                description="Created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                    }
                )
            ),
            400: openapi.Response(
                description="Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            500: openapi.Response(
                description="Server Error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        },
        tags=['Focal Point functions']
    )
    def create(self, request, *args, **kwargs):
        try:
            name = request.data.get('name')
            if not name:
                return Response(
                    {"error": "Name is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = self.get_serializer(data={'name': name})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            create_system_log(assign_user(request.user), f"Create new focal function: {name}")
            
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
        operation_description="Update a focal function",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            201: openapi.Response(
                description="Created",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                    }
                )
            ),
            400: openapi.Response(
                description="Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            500: openapi.Response(
                description="Server Error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        },
        tags=['Focal Point functions']
    )
    def update(self, request, *args, **kwargs):
        try:
            name = request.data.get('name')
            if not name:
                return Response(
                    {"error": "Name is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            function = self.get_object()
            serializer = self.get_serializer(function, data={'name': name}, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            create_system_log(assign_user(request.user), f"Update focal function {function.id}")
            
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
        operation_description="Delete a focal function",
        responses={
            204: "Successfully deleted",
            404: "Not found"
        },
        tags=['Focal Point functions']
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            create_system_log(assign_user(request.user), f"Delete focal function: {instance.name}")
            
            return Response({"success": True},status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_400_BAD_REQUEST
            )



class FocalPointViewSet(viewsets.ModelViewSet):
    queryset = FocalPoint.objects.all()
    serializer_class = FocalPointSerializer
    lookup_field = 'id'
    http_method_names = ["get", "put", "post", "delete"]

    def get_permissions(self):
        permission_map = {
            'list': 'focal_points_view',
            'retrieve': 'focal_points_view',
            'create': 'focal_points_create',
            'update': 'focal_points_edit',
            'destroy': 'focal_points_delete',
            'search': 'focal_points_view',
            'by_function': 'focal_points_view',
            'active': 'focal_points_view',
            'toogle_status': 'focal_points_toggle'
        }
        
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]


    @swagger_auto_schema(
        operation_description="List all focal points",
        responses={
            200: FocalPointSerializer
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new focal point",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['full_name', 'function', 'phone_number', 'email'],
            properties={
                'full_name': openapi.Schema(type=openapi.TYPE_STRING),
                'function': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
                'phone_number': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_STRING,
                        pattern=r'^\+?1?\d{9,15}$')
                    
                ),
                'email': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            201: FocalPointSerializer,
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        }
    )
    def create(self, request, *args, **kwargs):
        try:
            error, data = assignment_check({'full_name', 'function', 'phone_number', 'email'}, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not FocalFunction.objects.filter(id=data['function']).exists():
                return Response(
                    {"error": "Invalid function ID"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            phone_number = data['phone_number']
            if isinstance(phone_number, str):
                phone_number = phone_number.split(',')
            
            data['phone_number'] = phone_number
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            create_system_log(assign_user(request.user), f"create focal point {data['full_name']}")
            
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
        operation_description="Retrieve a focal point",
        responses={
            200: FocalPointSerializer,
            404: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a focal point",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'full_name': openapi.Schema(type=openapi.TYPE_STRING),
                'function': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
                'phone_number': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(
                        type=openapi.TYPE_STRING,
                        pattern=r'^\+?1?\d{9,15}$')
                    
                ),
                'email': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: FocalPointSerializer,
            400: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        }
    )
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            error, data = assignment_check({'full_name', 'function', 'phone_number', 'email'}, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            
            if not FocalFunction.objects.filter(id=data['function']).exists():
                return Response(
                    {"error": "Invalid function ID"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            phone_number = data['phone_number']
            if isinstance(phone_number, str):
                phone_number = phone_number.split(',')
            data['phone_number'] = phone_number
            
            serializer = self.get_serializer(instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            create_system_log(assign_user(request.user), f"Update focal point {instance.id}")
            
            return Response(serializer.data)
        
        except ValidationError as e:
            return Response(
                {"error": str_exception(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"}, 
                status=status.HTTP_400_BAD_REQUEST
            )


    @swagger_auto_schema(
        operation_description="Delete a focal point",
        responses={
            204: "Successfully deleted",
            404: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        }
    )
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            create_system_log(assign_user(request.user), f"Delete focal point {instance.full_name}")
            
            return Response(
                {"success": True}, 
                status=status.HTTP_204_NO_CONTENT
            )
        except ValidationError as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Search focal points",
        manual_parameters=[
            openapi.Parameter(
                'query',
                openapi.IN_QUERY,
                description="Search query (name, email, phone)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: FocalPointListSerializer,
            400: openapi.Response(
                description="Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            500: openapi.Response(
                description="Server Error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search focal points"""
        try:
            query = request.query_params.get('query', '')
            if not query:
                return Response(
                    {"error": "Search query is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            focal_points = FocalPoint.objects.filter(
                Q(full_name__icontains=query) |
                Q(email__icontains=query) |
                Q(phone_number__icontains=query)
            )
            
            serializer = FocalPointListSerializer(focal_points, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Get focal points active by function",
        manual_parameters=[
            openapi.Parameter(
                'function_id',
                openapi.IN_QUERY,
                description="Function ID (UUID)",
                type=openapi.TYPE_STRING,
                format='uuid',
                required=True
            )
        ],
        responses={
            200: FocalPointListSerializer,
            400: openapi.Response(
                description="Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            500: openapi.Response(
                description="Server Error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['get'])
    def by_function(self, request):
        """Get focal points active  by function"""
        try:
            function_id = request.query_params.get('function_id')
            
            if not function_id:
                return Response(
                    {"error": "Function ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            try:
                function = FocalFunction.objects.get(id=function_id)
            except FocalFunction.DoesNotExist:
                return Response(
                    {"error": "Function not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            focal_points = FocalPoint.objects.filter(function=function, is_active=True)
            serializer = FocalPointListSerializer(focal_points, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



    @swagger_auto_schema(
        operation_description="Get only active focal points",
        request_body=None,
        responses={
            200: FocalPointSerializer,
            400: openapi.Response(
                description="Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active focal points"""
        try:
            focal_points = FocalPoint.objects.filter(is_active=True)
            serializer = FocalPointSerializer(focal_points, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @swagger_auto_schema(
        operation_description="Toggle focal point active status",
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
        }
    )
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, id=None):
        """Toggle focal point active status"""
        try:
            focal_point = self.get_object()
            focal_point.is_active = not focal_point.is_active
            focal_point.updated_at = timezone.now()
            focal_point.save()
            create_system_log(assign_user(request.user), f"toggle focal point status: {focal_point.full_name}")
           
            return Response(
                {"success": True, "is_active": focal_point.is_active}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )