from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from apps.alertes.models import Alert
from drf_yasg import openapi
from core.common_function import str_exception
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from apps.roles.permissions import HasPermission
import base64
import binascii
from apps.mail_setting.tasks import send_email_task
from apps.users.models import User
from .serializers import EmailSenderSerializer
from core.common_function import  *
from apps.logsFonc.utils import create_system_log


class AlertEmailingView(views.APIView):
    def get_permissions(self):
        """Get required permissions based on action"""
        http_method_names = ['get']
        permission_map = {
            'GET': ['alerts_view', 'focal_points_view'],
        }
        
        permission_code = permission_map.get(self.request.method)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]
    @swagger_auto_schema(
        operation_description="Retrieves the alert template and the emails of the associated focal points",
        manual_parameters=[
            openapi.Parameter(
                'alert_id',
                openapi.IN_PATH,
                description="Aert ID",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Success",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'template': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Alert content"
                        ),
                        'focal_points_emails': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="List of focal point email"
                        )
                    }
                )
            ),
            404: openapi.Response(
                description="Alert not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            500: "Server Error"
        }
    )
    def get(self, request, alert_id):
        try:
            
            alert = Alert.objects.select_related('entity').get(id=alert_id)
            
            focal_points_emails = list(
                alert.entity.focal_points.filter(is_active=True).values_list('email', flat=True)
            )

            return Response({
                'template': alert.templates,
                'focal_points_emails': focal_points_emails,
                'subject': alert.get_alert_type_display(),
            })

        except Alert.DoesNotExist:
            return Response(
                {'error': 'Alert not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

  
class SendAlertEmailView(views.APIView):
    MAX_ATTACHMENT_SIZE = 1 * 1024 * 1024

    def get_permissions(self):
        permission_map = {
            'POST': 'alerts_send_email',
            # 'POST': 'alerts_view',
        }
        permission_code = permission_map.get(self.request.method)
        return [IsAuthenticated(), HasPermission(permission_code)] if permission_code else [IsAuthenticated()]

    def validate_attachment(self, attachment):
        try:
            content = base64.b64decode(attachment['content'])
            
            if len(content) > self.MAX_ATTACHMENT_SIZE:
                raise ValidationError(f"File size exceeds limit {self.MAX_ATTACHMENT_SIZE/1024/1024}Mo")
                
            return content
        except binascii.Error:
            raise ValidationError("The attachment content is not a valid base64 format")
        except KeyError:
            raise ValidationError("Invalid attachment format")

    def validate_recipients(self, alert, to_email, cc_emails, bcc_emails):
        
        focal_points_emails = set(
            alert.entity.focal_points.filter(is_active=True).values_list('email', flat=True)
        )
        user_emails = set(User.objects.values_list('email', flat=True))
        valid_emails = focal_points_emails.union(user_emails)

        
        if to_email not in focal_points_emails:
            raise ValidationError("The primary recipient must be a focal point affiliated with the entity concerned by the alert.")

        
        invalid_cc = [email for email in cc_emails if email not in valid_emails]
        if invalid_cc:
            raise ValidationError(f"Emails CC invalides: {', '.join(invalid_cc)}")

        invalid_bcc = [email for email in bcc_emails if email not in valid_emails]
        if invalid_bcc:
            raise ValidationError(f"Emails BCC invalides: {', '.join(invalid_bcc)}")

    @swagger_auto_schema(
        operation_description="Send an email regarding an alert",
        request_body=EmailSenderSerializer,
        responses={
            200: openapi.Response(
                description="Email sent successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'email_log_id': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                description="Invalid request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            404: "Alert dont found"
        }
    )
    def post(self, request, alert_id):
        try:
            
            try:
                alert = Alert.objects.select_related('entity').get(id=alert_id)
            except Alert.DoesNotExist:
                return Response(
                    {'error': 'Alert dont found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            error, data = assignment_check({"subject", "to", "body"}, request.data.items())
            if error:
                return Response(
                    {'error': data},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = EmailSenderSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'error': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            data = serializer.validated_data
            
            try:
                self.validate_recipients(
                    alert,
                    data['to'],
                    data.get('cc', []),
                    data.get('bcc', [])
                )
            except ValidationError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

            
            validated_attachments = []
            for attachment in data.get('attachments', []):
                try:
                    content = self.validate_attachment(attachment)
                    validated_attachments.append({
                        'filename': attachment['filename'],
                        'content': content,
                        'content_type': attachment.get('content_type', 'application/octet-stream')
                    })
                except ValidationError as e:
                    return Response(
                        {'error': f"Attachment error: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            send_email_task.delay(
                subject=data.get("subject", 'subject'),
                body=data.get("body", "body"),
                to_recipients=[data.get('to',[])] ,
                cc_recipients=data.get('cc', []),
                bcc_recipients=data.get('bcc', []),
                attachments=data.get("attachments", []),
                is_html=True,
            )
            create_system_log(assign_user(request.user), f"Attempt to send email about alert {alert.id}: {alert.get_alert_type_display()} - {alert.platform.url}")
            return Response(
                {'message': 'Attempt to send triggered email, please check logs for status. If email settings is not enabled, no email will be sent.'},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {'error': "An error occured processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
  