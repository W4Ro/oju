from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from .models import AVVendor
from .serializers import AVVendorSerializer
from apps.roles.permissions import HasPermission
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.common_function import *
from apps.logsFonc.utils import create_system_log

class AVVendorViewSet(viewsets.ModelViewSet):
    serializer_class = AVVendorSerializer
    queryset = AVVendor.objects.all()
    lookup_field = 'id'
    http_method_names = ['get', 'put', 'post', 'delete']
    
    def get_permissions(self):
        """Get required permissions based on action"""
        permission_map = {
            'list': 'vendor_list_view',
            'retrieve': 'vendor_list_view',
            'create': 'vendor_list_create',
            'update': 'vendor_list_edit',
            'destroy': 'vendor_list_delete'
        }
        
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]

    @swagger_auto_schema(
        operation_description="List all AV vendors",
        request_body=None,
        responses={
            200: AVVendorSerializer(many=True)
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new AV vendor",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name', 'contact'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'contact': openapi.Schema(type=openapi.TYPE_STRING),
                'comments': openapi.Schema(type=openapi.TYPE_STRING)
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
                        'contact': openapi.Schema(type=openapi.TYPE_STRING),
                        'comments': openapi.Schema(type=openapi.TYPE_STRING),
                        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                    }
                )
            ),
            400: "Bad Request",
            500: "Server Error"
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new AV Vendor"""
        try:
            error, data = assignment_check({'name', 'contact', 'comments'}, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            create_system_log(assign_user(request.user), f"Create new AV Vendor: {data['name']}")
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
        operation_description="Update an AV vendor",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING),
                'contact': openapi.Schema(type=openapi.TYPE_STRING),
                'comments': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            201: openapi.Response(
                description="Updated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                        'contact': openapi.Schema(type=openapi.TYPE_STRING),
                        'comments': openapi.Schema(type=openapi.TYPE_STRING),
                        'created_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                        'updated_at': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                    }
                )
            ),
            400: "Bad Request",
            500: "Server Error"
        }
    )
    def update(self, request, *args, **kwargs):
        """Update an AV Vendor"""
        try:
            instance = self.get_object()
            
            error, data = assignment_check({'name', 'contact', 'comments'}, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            create_system_log(assign_user(request.user), f"Update AV Vendor : ({instance.name})")
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
        operation_description="Delete an AV vendor",
        responses={
            204: "Successfully deleted",
            404: "Not found",
            500: "Internal Server Error"
        }
    )
    def destroy(self, request, *args, **kwargs):
        try:
            av_vendor = self.get_object()
            av_vendor.delete()
            create_system_log(assign_user(request.user), f"Delete AV Vendor {av_vendor.name}")
            
            return Response({"success": True},status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {"error": f"Failed to delete AV vendor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )