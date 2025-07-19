from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.exceptions import ValidationError
from apps.roles.permissions import HasPermission
from apps.logsFonc.utils import create_system_log
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from core.common_function import *
from core.definitions import *
from django.core.cache import cache

from .models import (
    Scan, SSLScanCriteria, DomainScanCriteria, DefacementScanCriteria,
    WhitelistedDomain, WebsiteScanCriteria
)
from .serializers import (
    ScanSerializer, SSLScanCriteriaSerializer, DomainScanCriteriaSerializer,
    DefacementScanCriteriaSerializer, UpdateMaxResponseTimeSerializer,
    WebsiteScanCriteriaSerializer, DefacementScanCriteriaUpdateSerializer
)



class ScanViewSet(viewsets.ViewSet):
    """
    API endpoint to manage scan types.
    """
    queryset = Scan.objects.all()
    serializer_class = ScanSerializer
    http_method_names = ['get', "post"]

    def get_permissions(self):
        """Get required permissions based on action"""
        permission_map = {
            'list': 'cerb_scans_view',
            'toggle_active': 'cerb_scans_toggle',
            'get_criteria': 'cerb_scans_view',
        }
        
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]

    @swagger_auto_schema(
        operation_description="List all available scans",
        responses={
            200: ScanSerializer(many=True),
            500: "Server Error"
        },
        tags=['SubScan']
    )
    def list(self, request):
        """
        List all available scans.
        """
        try:
            scans = Scan.objects.all()
            serializer = ScanSerializer(scans, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @swagger_auto_schema(
        operation_description="Get criteria for a specific scan",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'scan': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'code': openapi.Schema(type=openapi.TYPE_STRING),
                            'description': openapi.Schema(type=openapi.TYPE_STRING),
                            'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        }
                    ),
                    'criteria': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={}
                    )
                }
            )
            ,
            404: "Scan not found",
            500: "Server Error"
        },
        tags=['SubScan']
    )
    @action(detail=False, methods=['get'], url_path='(?P<scan_code>[^/.]+)/criteria')
    def get_criteria(self, request, scan_code=None):
        """
        Get criteria for a specific scan identified by its code.
        """
        try:
            scan = get_object_or_404(Scan, code=scan_code)
            scan_data = ScanSerializer(scan).data
            criteria_data = None
            
            if scan.code == 'ssl' and hasattr(scan, 'ssl_criteria'):
                criteria_data = SSLScanCriteriaSerializer(scan.ssl_criteria).data
            
            elif scan.code == 'domain' and hasattr(scan, 'domain_criteria'):
                criteria_data = DomainScanCriteriaSerializer(scan.domain_criteria).data
            
            elif scan.code == 'defacement' and hasattr(scan, 'defacement_criteria'):
                criteria_data = DefacementScanCriteriaSerializer(scan.defacement_criteria).data
            
            elif scan.code == 'website' and hasattr(scan, 'website_criteria'):
                criteria_data = WebsiteScanCriteriaSerializer(scan.website_criteria).data
            
            return Response(
                {
                    'scan': scan_data,
                    'criteria': criteria_data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_description="Activate or deactivate a scan",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                }
            ),
            404: "Scan not found",
            500: "Server Error"
        },
        tags=['SubScan']
    )
    @action(detail=False, methods=['post'], url_path='(?P<scan_code>[^/.]+)/toggle')
    def toggle_active(self, request, scan_code=None):
        """
        Activate or deactivate a scan.
        """
        try:
            scan = get_object_or_404(Scan, code=scan_code)
            
            scan.is_active = not scan.is_active
            scan.save()
            create_system_log(assign_user(request.user), f"Toggle scan {scan.name} status")
            return Response(
                {
                    'name': scan.name,
                    'is_active': scan.is_active,
                    "success": True
                }, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"},
                status=status.HTTP_404_NOT_FOUND
            )


class SSLScanCriteriaViewSet(viewsets.ModelViewSet):
    """
    API endpoint to manage SSL scan criteria.
    """
    queryset = SSLScanCriteria.objects.all()
    serializer_class = SSLScanCriteriaSerializer
    http_method_names = ["post"]

    def get_permissions(self):
        """Get required permissions based on action"""
        permission_map = {
            'toggle_check_ssl_error': 'cerb_scans_manage',
            'toggle_check_ssl_expiry': 'cerb_scans_manage',
        }
        
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]

    def get_object(self):
        return SSLScanCriteria.objects.first()

    @swagger_auto_schema(
        request_body=None,
        operation_description="Enable or disable SSL error checking",
        responses={
            200: openapi.Response(
                description="Criterion successfully updated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'check_ssl_error': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            400: "Bad Request",
            404: "Not Found",
            500: "Server Error"
        },
        tags=['SSLScan']
    )
    @action(detail=True, methods=['post'])
    def toggle_check_ssl_error(self, request, pk=None):
        """
        Enable or disable SSL error checking.
        """
        try:
            criteria = self.get_object()
            criteria.check_ssl_error = not criteria.check_ssl_error
            criteria.save()
            
            create_system_log(
                assign_user(request.user), 
                f"Toggle SSL error checking status"
            )
                
            return Response({
                'check_ssl_error': criteria.check_ssl_error,
                'success': True
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @swagger_auto_schema(
        request_body=None,
        operation_description="Enable or disable SSL expiry checking",
        responses={
            200: openapi.Response(
                description="Criterion successfully updated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'check_ssl_expiry': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            400: "Bad Request",
            404: "Not Found",
            500: "Server Error"
        },
        tags=['SSLScan']
    )
    @action(detail=True, methods=['post'])
    def toggle_check_ssl_expiry(self, request, pk=None):
        """
        Enable or disable SSL expiry checking.
        """
        try:
            criteria = self.get_object()
            criteria.check_ssl_expiry = not criteria.check_ssl_expiry
            criteria.save()
            
            create_system_log(
                assign_user(request.user), 
                f"Toggle SSL expiry checking to status"
            )
                
            return Response({
                'check_ssl_expiry': criteria.check_ssl_expiry,
                'success': True
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DomainScanCriteriaViewSet(viewsets.ModelViewSet):
    """
    API endpoint pour gérer les critères du scan de disponibilité de domaine.
    """
    queryset = DomainScanCriteria.objects.all()
    serializer_class = DomainScanCriteriaSerializer
    http_method_names = ["post"]

    def get_permissions(self):
        """Get required permissions based on action"""
        permission_map = {
            'toggle_check_whois': 'cerb_scans_manage',
            'toggle_check_dns_servers': 'cerb_scans_manage',
            'toggle_check_ip_mismatch_error': 'cerb_scans_manage',
            'toggle_check_domain_expiry_error': 'cerb_scans_manage',
        }
        
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]

    def get_object(self):
        return DomainScanCriteria.objects.first()
    
    @swagger_auto_schema(
        request_body=None,
        operation_description="Enable or disable WHOIS checking",
        responses={
            200: openapi.Response(
                description="Criterion successfully updated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'check_whois': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            400: "Bad Request",
            404: "Not Found",
            500: "Server Error"
        },
        tags=['DomainScan']
    )
    @action(detail=True, methods=['post'])
    def toggle_check_whois(self, request, pk=None):
        """
        Enable or disable WHOIS checking.
        """
        try:
            criteria = self.get_object()
            criteria.check_whois = not criteria.check_whois
            criteria.save()
        
            create_system_log(
                assign_user(request.user), 
                f"Toggle WHOIS checking status"
            )
                
            return Response({
                'check_whois': criteria.check_whois,
                'success': True
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        request_body=None,
        operation_description="Enable or disable DNS servers checking",
        responses={
            200: openapi.Response(
                description="Criterion successfully updated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'check_dns_servers': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            400: "Bad Request",
            404: "Not Found",
            500: "Server Error"
        },
        tags=['DomainScan']
    )
    @action(detail=True, methods=['post'])
    def toggle_check_dns_servers(self, request, pk=None):
        """
        Enable or disable DNS servers checking.
        """
        try:
            criteria = self.get_object()
            criteria.check_dns_servers = not criteria.check_dns_servers
            criteria.save()
            
            create_system_log(
                assign_user(request.user), 
                f"Toggle DNS servers checking status"
                )
                
            return Response({
                'check_dns_servers': criteria.check_dns_servers,
                'success': True
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        request_body=None,
        operation_description="Enable or disable domain expiry error checking",
        responses={
            200: openapi.Response(
                description="Criterion successfully updated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'check_domain_expiry_error': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            400: "Bad Request",
            404: "Not Found",
            500: "Server Error"
        },
        tags=['DomainScan']
    )
    @action(detail=True, methods=['post'])
    def toggle_check_domain_expiry_error(self, request, pk=None):
        """
        Enable or disable domain expiry error checking.
        """
        try:
            criteria = self.get_object()
            criteria.check_domain_expiry_error = not criteria.check_domain_expiry_error
            criteria.save()
            
            
            create_system_log(
                assign_user(request.user), 
                f"Toggle domain expiry error checking status"
            )
                
            return Response({
                'check_domain_expiry_error': criteria.check_domain_expiry_error,
                'success': True
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DefacementScanCriteriaViewSet(viewsets.ModelViewSet):
    """
    API endpoint to manage defacement scan criteria.
    """
    queryset = DefacementScanCriteria.objects.all()
    serializer_class = DefacementScanCriteriaSerializer
    http_method_names = ["post"]

    def get_permissions(self):
        """Get required permissions based on action"""
        permission_map = {
            'update_criteria': 'cerb_scans_manage',
        }
        
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]

    def get_object(self):
        return DefacementScanCriteria.objects.first()

    @swagger_auto_schema(
        request_body=DefacementScanCriteriaUpdateSerializer,
        operation_description="Update all defacement scan criteria",
        responses={
            200: openapi.Response(
                description="Criteria successfully updated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'acceptance_rate': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'whitelisted_domains': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        ),
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            400: "Bad Request",
            404: "Not Found",
            500: "Server Error"
        },
        tags=['DefacementScan']
    )
    @action(detail=True, methods=['post'])
    def update_criteria(self, request, pk=None):
        """
        Update all defacement scan criteria including acceptance rate and whitelisted domains.
        This endpoint removes all previous whitelisted domains and adds the new ones.
        """
        try:
            error, data = assignment_check({'acceptance_rate', 'whitelisted_domains'}, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not isinstance(data.get("acceptance_rate", 0), int):
                return Response(
                    {"error": "acceptance_rate must be valid Integer"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not 0 <= data.get('acceptance_rate') <=5000:
                return Response(
                    {"error": "Invalid acceptance_rate value, must be between 0 and 5000"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not isinstance(data.get("whitelisted_domains", []), list):
                return Response(
                    {"error": "whitelisted_domains must be a valid list"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not 1 <= len(data.get("whitelisted_domains", [])) <=200:
                return Response(
                    {"error": "whitelisted_domains must be between 1 and 200"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            criteria = self.get_object()
            serializer = DefacementScanCriteriaUpdateSerializer(data=data)
            
            serializer.is_valid(raise_exception=True)
            criteria.acceptance_rate = serializer.validated_data['acceptance_rate']
            criteria.save()
            
            new_domains = serializer.validated_data.get('whitelisted_domains', [])
            
            WhitelistedDomain.objects.filter(defacement_criteria=criteria).delete()
            
            created_domains = []
            for domain in new_domains:
                WhitelistedDomain.objects.create(
                    defacement_criteria=criteria,
                    domain=domain
                )
                created_domains.append(domain)
            
            create_system_log(
                assign_user(request.user), 
                f"Updated defacement criteria"
            )
            cache.delete(SIZE_TOLERANCE_CACHE_KEY)
            cache.delete(WHITELIST_DOMAINS_CACHE_KEY)
            return Response({
                'success': True
            }, status=status.HTTP_200_OK)
           
                
        except ValidationError as e:
            return Response(
                    {"error": str_exception(e), "success": False},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class WebsiteScanCriteriaViewSet(viewsets.ModelViewSet):
    """
    API endpoint to manage website availability scan criteria.
    """
    queryset = WebsiteScanCriteria.objects.all()
    serializer_class = WebsiteScanCriteriaSerializer
    
    def get_permissions(self):
        """Get required permissions based on action"""
        permission_map = {
            'update_max_response_time': 'cerb_scans_manage',
        }
        
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]


    def get_object(self):
        return WebsiteScanCriteria.objects.first()

    @swagger_auto_schema(
        request_body=UpdateMaxResponseTimeSerializer,
        operation_description="Update maximum acceptable response time",
        responses={
            200: openapi.Response(
                description="Maximum response time successfully updated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'max_response_time_ms': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            400: "Bad Request",
            404: "Not Found",
            500: "Server Error"
        },
        tags=['WebsiteScan']
    )
    @action(detail=True, methods=['post'])
    def update_max_response_time(self, request, pk=None):
        """
        Update the maximum acceptable response time.
        """
        try:
            error, data = assignment_check({'max_response_time_ms'}, request.data.items())
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not isinstance(data.get("max_response_time_ms", 0), int):
                return Response(
                    {"error": "max_response_time_ms must be valid Integer"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            criteria = self.get_object()
            serializer = UpdateMaxResponseTimeSerializer(data=data)
            if not 1000 <= data['max_response_time_ms'] <=60000:
                return Response(
                {"error": 'value must be between 1000 and 60000 ms'},
                status=status.HTTP_400_BAD_REQUEST
            )
            serializer.is_valid(raise_exception=True)
            criteria.max_response_time_ms = serializer.validated_data['max_response_time_ms']
            criteria.save()
            
            create_system_log(
                assign_user(request.user), 
                f"Updated max response time for website scan criteria"
            )
                
            return Response({
                'max_response_time_ms': criteria.max_response_time_ms,
                'success': True
            }, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response(
                {"error": str_exception(e), "success": False},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {"error": "An error occured processing your request", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

