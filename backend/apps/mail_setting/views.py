from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import MailConfig
from .serializers import MailConfigSerializer
from .utils import rate_limit_mail_config
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.exceptions import ValidationError
from core.common_function import *
from django.utils import timezone
import socket, smtplib
from apps.roles.permissions import HasPermission
from apps.logsFonc.utils import create_system_log
from rest_framework.permissions import IsAuthenticated


class MailConfigViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = MailConfig.objects.all()
    serializer_class = MailConfigSerializer
    http_method_names = ["get", "put", "post"]


    def test_connection(self, smtp_server, smtp_port, use_ssl, use_tls, email_host, email_password):
        """
        Test the SMTP connection with current configuration
        Returns (success: bool, error_message: str)
        """
        try:
            
            socket.gethostbyname(smtp_server)

            if use_ssl:
                server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=5)
            else:
                server = smtplib.SMTP(smtp_server, smtp_port, timeout=5)

            if use_tls:
                server.starttls()

            server.login(email_host, email_password)
            server.quit()

            
            return True, "Connection test successful"

        except socket.gaierror:
            error_msg = f"DNS or connection error"
            return False, error_msg

        except socket.timeout:
            return False, f"Connection timed out"

        except smtplib.SMTPAuthenticationError:
            error_msg = "Authentication failed: Invalid credentials"
            return False, error_msg

        except ConnectionRefusedError:
            return False, f"Connection refused to {smtp_server}:{smtp_port}"
        
        except Exception as e:
            error_msg = f"Connection test failed: {str(e)}"
            return False, error_msg

    def get_queryset(self):
        return MailConfig.objects.all()

    def get_permissions(self):
        """Get required permissions based on action"""
        permission_map = {
            'list': 'mail_settings_view',
            'update': 'mail_settings_edit',
            'toggle_status': 'mail_settings_toggle'
        }
        
        permission_code = permission_map.get(self.action)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]

    @swagger_auto_schema(
        operation_description="Return mail configurations",
        request_body=None,
        responses={
            200: openapi.Response(
                description="Success",
                schema=MailConfigSerializer(many=False)
            )
        }
    )
    def list(self, request, *args, **kwargs):
        """Return the single mail configurations"""
        config = MailConfig.objects.first()
        if not config:
            return Response(
                {"detail": "No mail configurations found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(config)
        return Response(serializer.data)


    @swagger_auto_schema(
        operation_description="Update mail configurations",
        request_body=MailConfigSerializer,
        responses={
            200: openapi.Response(
                description="Success",
                schema=MailConfigSerializer(many=False)
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
    @rate_limit_mail_config(max_attempts=2, timeout_seconds=60)
    def update(self, request, *args, **kwargs):
        """Update mail configurations"""
        try:
            instance = MailConfig.objects.first()
            if not instance:
                return Response(
                    {"detail": "No mail configuration found to update"},
                    status=status.HTTP_404_NOT_FOUND
                )
            error, data = assignment_check({'smtp_server', 'smtp_port', 'use_tls', 'use_ssl', 'email_host', 'email_password', 'default_sender_name', 'is_active'}, request.data.items())
            
            if error:
                return Response(
                    {"error": data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if 'use_tls' not in data:
                data['use_tls'] = False
            if 'use_ssl' not in data:
                data['use_ssl'] = False
            
            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)

            success, message = self.test_connection(
                smtp_server=serializer.validated_data.get("smtp_server"),
                smtp_port=serializer.validated_data.get("smtp_port"),
                use_ssl=serializer.validated_data.get("use_ssl"),
                use_tls=serializer.validated_data.get("use_tls"),
                email_host=serializer.validated_data.get("email_host"),
                email_password=serializer.validated_data.get("email_password"),
            )

            if not success:
                return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
            
            self.perform_update(serializer)
            create_system_log(assign_user(request.user), f"Update mail setting")
            
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
        operation_description="Toggle active status of mail configuration",
        request_body=None,
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                )
            ),
            404: openapi.Response(
                description="Not Found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            500: "Server Error"
        }
    )
    @action(detail=False, methods=['post'])
    def toggle_status(self, request):
        """Toggle the active status of mail configuration"""
        try:
            config = MailConfig.objects.first()
            if not config:
                return Response(
                    {"detail": "No mail configuration found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            if not config.is_active:
                success, message = self.test_connection(
                    smtp_server=config.smtp_server,
                    smtp_port=config.smtp_port,
                    use_ssl=config.use_ssl,
                    use_tls=config.use_tls,
                    email_host=config.email_host,
                    email_password=config.email_password,
                )
                if not success:
                    return Response(
                        {"error": f"Can not activate emailing : {message}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            config.is_active = not config.is_active
            config.updated_at = timezone.now()
            config.save()
            create_system_log(assign_user(request.user), f"Toogle mail setting status")
            
            return Response({
                "success": True,
                "is_active": config.is_active
            })
        except Exception as e:
            return Response(
                {"error": "An error occured processing your request"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

