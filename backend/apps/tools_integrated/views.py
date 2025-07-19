from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Integration, RTIR, Cerebrate, VirusTotal
from apps.logsFonc.utils import create_system_log
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.common_function import *
from rest_framework.exceptions import ValidationError
from .tasks import refresh_cerebrate
from .utils import rate_limit_refresh
from .serializers import (
    IntegrationSerializer, RTIRSerializer, RTIRUpdateSerializer,
    CerebrateSerializer, CerebrateUpdateSerializer, VirusTotalSerializer, VirusTotalUpdateSerializer
)
from asgiref.sync import async_to_sync
from apps.roles.permissions import HasPermission
from .rtir import RTIRClient
from .cerebrate import CerebrateAPI
from .virustotal import VirusTotalScanner
import logging

logger= logging.getLogger(__name__)


class IntegrationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to display available integrations.
    Read-only as integrations are fixed.
    """
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer
    http_method_names = ["get"]

    def get_permissions(self):
        permission_map = {
            'list': 'integrations_view',
            'retrieve': 'integrations_view',
        }
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]


    @swagger_auto_schema(
        operation_summary="List of integrations",
        operation_description="""
        Returns the list of available integrations with their status.
        For each integration, returns:
        - The name of the tool
        - Its description
        - Its activation status
        - Its last update date
        """,
        responses={
            200: IntegrationSerializer(many=True),
            401: "Not authenticated"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Detail of an integration",
        operation_description="Returns details of a specific integration",
        responses={
            200: IntegrationSerializer(),
            404: "Integration not found",
            401: "Not authenticated"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class RTIRViewSet(viewsets.GenericViewSet):
    """
    ViewSet to manage RTIR configuration.
    Allows to view and modify the configuration.
    """
    queryset = RTIR.objects.all()
    serializer_class = RTIRSerializer

    def get_permissions(self):
        permission_map = {
            'list': 'integrations_view',
            'retrieve': 'integrations_view',
            'toggle_status': 'integrations_toggle',
            'update': 'integrations_edit'
        }
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]


    def get_serializer_class(self):
        if self.action in ['update']:
            return RTIRUpdateSerializer
        return RTIRSerializer

    def get_object(self):
        return RTIR.objects.first()

    @swagger_auto_schema(
        operation_summary="Get RTIR Configuration",
        operation_description="""
        Returns the current RTIR configuration.
        The password is never returned.
        """,
        request_body=None,
        responses={
            200: RTIRSerializer(),
            404: "No configuration found",
            401: "Not authenticated"
        },
        tags=["RTIR"]
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response(
                {"error": "No RTIR configuration found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Update RTIR configuration",
        operation_description="""
        Update RTIR configuration.
            - Check connection before updating
            - Password is not returned in response
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['url', 'username', 'password'],
            properties={
                'url': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="RTIR server URL (must start with http:// or https://)"
                ),
                'username': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="username"
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="password"
                ),
            }
        ),
        responses={
            200: RTIRSerializer(),
            400: "Invalid data or login failure",
            404: "Configuration not found",
            401: "Not authenticated"
        },
        tags=["RTIR"]
    )
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if not instance:
                return Response(
                    {"error": "No RTIR configuration found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            error, data = assignment_check({'url', 'username', 'password'}, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(instance, data=data, partial=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            create_system_log(assign_user(request.user), f"update RTIR configurations")
            return Response(RTIRSerializer(instance).data)

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
        operation_summary="Toggle activation state",
        operation_description="Enables or disables RTIR integration",
        request_body=None,
        responses={
            200: RTIRSerializer(),
            404: "Configuration not found",
            401: "Not authenticated"
        },
        tags=["RTIR"]
    )
    @action(detail=False, methods=['post'])
    def toggle_status(self, request):
        try:
            instance = self.get_object()
            if not instance:
                return Response(
                    {"error": "No RTIR configuration found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            if not instance.is_active:
                test_rtir = RTIRClient(instance.url, instance.username, instance.password)
                if not test_rtir.authenticate():
                    return Response(
                        {"error": "invalid RTIR data to authenticate"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            instance.is_active = not instance.is_active
            instance.save()
            create_system_log(assign_user(request.user), "Toggle RTIR status")
            return Response(RTIRSerializer(instance).data)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CerebrateViewSet(viewsets.GenericViewSet):
    queryset = Cerebrate.objects.all()
    serializer_class = CerebrateSerializer

    def get_permissions(self):
        permission_map = {
            'list': 'integrations_view',
            'retrieve': 'integrations_view',
            'toggle_status': 'integrations_toggle',
            'update': 'integrations_edit',
            'refresh': 'integrations_edit'
        }
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]

    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return CerebrateUpdateSerializer
        return CerebrateSerializer

    def get_object(self):
        return Cerebrate.objects.first()
    
    @swagger_auto_schema(
        operation_summary="Get Cerebrate Setup",
        operation_description="Returns the current configuration of Cerebrate",
        request_body=None,
        responses={
            200: CerebrateSerializer(),
            404: "No configuration found"
        },
        tags=["Cerebrate"]
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response(
                {"error": "No Cerebrate configuration found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Update Cerebrate Configuration",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['url', 'api_key', 'refresh_frequency'],
            properties={
                'url': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Base URL of the Cerebrate server (must start with http:// or https://)"
                ),
                'api_key': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="API key for authentication"
                ),
                'refresh_frequency': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Refresh rate in seconds",
                    enum=[86400, 172800, 518400, 345600, 432000, 518400, 604800]
                )
            }
        ),
        responses={
            200: CerebrateSerializer,
            400: "Invalid data or connection failure",
            404: "Configuration not found"
        },
        tags=["Cerebrate"]
    )
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if not instance:
                return Response(
                    {"error": "No Cerebrate configuration found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            error, data = assignment_check({'url', 'api_key', 'refresh_frequency'}, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(instance, data=data, partial=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            create_system_log(assign_user(request.user), "Update cerebrate configuration")
            return Response(CerebrateSerializer(instance).data)
            
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
        operation_summary="Toggle activation state",
        operation_description="Enables or disables Cerebrate integration",
        request_body=None,
        responses={
            200: CerebrateSerializer,
            404: "Configuration not found"
        },
        tags=["Cerebrate"]
    )
    @action(detail=False, methods=['post'])
    def toggle_status(self, request):
        try:
            instance = self.get_object()
            if not instance:
                return Response(
                    {"error": "No Cerebrate configuration found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            if not instance.is_active:
                test_cerebrate = CerebrateAPI(instance.url, instance.api_key)
                if not test_cerebrate.check_connection():
                    return Response(
                        {"error": "invalid cerebrate config data to authenticate"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            instance.is_active = not instance.is_active
            instance.save()
            create_system_log(assign_user(request.user), "toggle cerebrate status")
            return Response(CerebrateSerializer(instance).data)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    

    @swagger_auto_schema(
        operation_summary="Refresh manually",
        operation_description="Triggers a manual refresh of Cerebrate data",
        request_body=None,
        responses={
            200: "Refresh triggered",
            404: "Configuration not found",
            400: "Error while refreshing",
            500: "Server error"
        },
        tags=["Cerebrate"]
    )
    @action(detail=False, methods=['post'])
    @rate_limit_refresh(timeout_seconds=3600)
    def refresh(self, request):
        instance = self.get_object()
        if not instance:
            return Response(
                {"error": "No Cerebrate configuration found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not instance.is_active:
            return Response(
                {"error": "Cerebrate integration is not active"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            refresh_cerebrate.delay()
            logger.info(f"Cerebrate manuel refresh task queud successfully by {request.user}")
            create_system_log(assign_user(request.user), "Queud cerebrate manuel refresh task")
            return Response(
                {"success": 'The refresh has been started, you can consult logs for more details'},
                 status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": "An error occurred while refreshing Cerebrate data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class VirusTotalViewSet(viewsets.GenericViewSet):
    queryset = VirusTotal.objects.all()
    serializer_class = VirusTotalSerializer

    def get_permissions(self):
        permission_map = {
            'list': 'integrations_view',
            'retrieve': 'integrations_view',
            'toggle_status': 'integrations_toggle',
            'update': 'integrations_edit',
        }
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]

    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return VirusTotalUpdateSerializer
        return VirusTotalSerializer

    def get_object(self):
        return VirusTotal.objects.first()
    
    @swagger_auto_schema(
        operation_summary="Get VirusTotal Setup",
        operation_description="Returns the current configuration of VirusTotal",
        request_body=None,
        responses={
            200: VirusTotalSerializer(),
            404: "No configuration found"
        },
        tags=["VirusTotal"]
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response(
                {"error": "No VirusTotal configuration found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Update VirusTotal Configuration",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['api_key', 'scan_frequency'],
            properties={
                'api_key': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="API key for authentication"
                ),
                'scan_frequency': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Scan frequency in seconds",
                    enum=[86400, 172800, 518400, 345600, 432000, 518400, 604800]
                )
            }
        ),
        responses={
            200: VirusTotalSerializer,
            400: "Invalid data or connection failure",
            404: "Configuration not found",
            500: "Server error"
        },
        tags=["VirusTotal"]
    )
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if not instance:
                return Response(
                    {"error": "No VirusTotal configuration found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            error, data = assignment_check({'api_key', 'scan_frequency'}, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(instance, data=data, partial=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            create_system_log(assign_user(request.user), "Update VirusTotal configuration")
            return Response(VirusTotalSerializer(instance).data)
            
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
        operation_summary="Toggle activation state",
        operation_description="Enables or disables VirusTotal integration",
        request_body=None,
        responses={
            200: VirusTotalSerializer,
            404: "Configuration not found"
        },
        tags=["VirusTotal"]
    )
    @action(detail=False, methods=['post'])
    def toggle_status(self, request):
        try:
            instance = self.get_object()
            if not instance:
                return Response(
                    {"error": "No VirusTotal configuration found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            if not instance.is_active:
                test_virustotal = VirusTotalScanner(instance.api_key)
                try:
                    async_to_sync(test_virustotal.verify_api_key)()
                except:
                    logger.error(f"Invalid VirusTotal data to authenticate by {request.user}")
                    return Response(
                        {"error": "invalid VirusTotal config data to authenticate"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            instance.is_active = not instance.is_active
            instance.save()
            create_system_log(assign_user(request.user), "toggle VirusTotal status")
            return Response(VirusTotalSerializer(instance).data)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    

