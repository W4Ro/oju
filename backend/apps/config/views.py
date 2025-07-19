from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Configuration
from .serializers import ConfigurationSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.exceptions import ValidationError
from apps.roles.permissions import HasPermission
from apps.logsFonc.utils import create_system_log
from rest_framework.permissions import IsAuthenticated
from core.common_function import *
from core.definitions import *
from django.core.cache import cache

class ConfigurationViewSet(viewsets.ModelViewSet):
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer
    http_method_names = ['get', 'put', 'post']

    def get_permissions(self):
        """Get required permissions based on action"""
        permission_map = {
            'retrieve': 'config_view',
            'update': 'config_edit',
            'toggle_proxy': 'config_toggle',
            'toggle_host': 'config_toggle',
            'toggle_alert': 'config_toggle',
        }
        
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]

    def get_object(self):
        return Configuration.objects.first()
    
    @swagger_auto_schema(
        operation_description="Get current configuration",
        responses={
            200: openapi.Response(
                description="Success",
                schema=ConfigurationSerializer(many=False)
            ),
            404: openapi.Response(
                description="Not Found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update configuration settings. Only email, proxy, user_agent, dns_server, max_worker and scan_frequency can be modified",
        request_body=ConfigurationSerializer,
        responses={
            200: openapi.Response(
                description="Success",
                schema=ConfigurationSerializer(many=False)
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
        }
    )
    def update(self, request, *args, **kwargs):
        """Handle partial updates for specific fields"""
        try:
            instance = Configuration.objects.first()
            if not instance:
                return Response(
                    {"error": "No configuration found, please run init_config"},
                    status=status.HTTP_404_NOT_FOUND
                )
            error, data = assignment_check({'email', 'dns_server', 'scan_frequency', 'user_agent', 'max_worker','receive_alert'}, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if 'proxy' in request.data:
                data['proxy'] = request.data['proxy']

                if not isinstance(data["proxy"], list):
                    return Response(
                        {"error": "Proxy might be a list"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                data['proxy'] = list(set(data['proxy']))

                
            if not isinstance(data["dns_server"], list):
                return Response(
                    {"error": "dns_server might be a list"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data['dns_server'] = list(set(data['dns_server']))
            serializer = self.get_serializer(
                instance,
                data=data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            create_system_log(assign_user(request.user), f"Update system configuration")
            cache.delete(DNS_SERVER_CACHE_KEY)
            return Response(serializer.data)
        
        except ValidationError as e:
            return Response(
                {"error": str_exception(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_400_500_INTERNAL_SERVER_ERROR
            )


    @swagger_auto_schema(
        operation_description="Toggle proxy usage state. Tests connection when enabling proxy.",
        responses={
            200: openapi.Response(
                description="Success",
                schema=ConfigurationSerializer(many=False)
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
        }
    )
    @action(detail=False, methods=['post'])
    def toggle_proxy(self, request):
        """Toggle use_proxy and test connection if enabling"""
        instance = self.get_object()
        if not instance:
            return Response(
                {"error":"No configuration found, please run init_config"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        new_use_proxy = not instance.use_proxy

        if new_use_proxy:
            serializer = self.get_serializer(
                instance,
                data={'use_proxy': True},
                partial=True
            )
            try:
                serializer.is_valid(raise_exception=True)
                create_system_log(assign_user(request.user), f"Activated proxy")
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
        else:
            create_system_log(assign_user(request.user), f"Desactivated proxy")
        

        instance.use_proxy = new_use_proxy
        instance.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Toggle use_host_on_proxy_fail usage state.",
        responses={
            200: openapi.Response(
                description="Success",
                schema=ConfigurationSerializer(many=False)
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
        }
    )
    @action(detail=False, methods=['post'])
    def toggle_host(self, request):
        """Toggle use_proxy and test connection if enabling"""
        try:
            instance = self.get_object()
            if not instance:
                return Response(
                    {"error":"No configuration found, please run init_config"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            instance.use_host_on_proxy_fail = not instance.use_host_on_proxy_fail
            instance.save()
            create_system_log(assign_user(request.user), f"Toggle host")
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @swagger_auto_schema(
        operation_description="Toggle receive_alert usage state.",
        responses={
            200: openapi.Response(
                description="Success",
                schema=ConfigurationSerializer(many=False)
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
        }
    )
    @action(detail=False, methods=['post'])
    def toggle_alert(self, request):
        """Toggle receive_alert status"""
        try:
            instance = self.get_object()
            if not instance:
                return Response(
                    {"error":"No configuration found, please run init_config"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            instance.receive_alert = not instance.receive_alert
            instance.save()
            create_system_log(assign_user(request.user), f"Toggle Alert")
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
