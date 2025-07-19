from django.template.loader import render_to_string
from apps.config.models import Configuration
from apps.mail_setting.tasks import send_email_task
from apps.tools_integrated.tasks import create_rtir_ticket
from django.utils.html import escape
import logging

logger = logging.getLogger(__name__)

class AlertNotificationService:
    """Service to manage alert notifications"""
    
    def __init__(self):
        config = Configuration.objects.first()
        if not config:
            return
        self.notification_email = config.email
        self.can_receiveAlert = config.receive_alert
        
    def send_alert_notification(self, alert):
        """
        Send an email notification and create an RTIR ticket for an alert
        
        Args:
            alert: Alert instance
        """
        try:
                        
            points_focaux = alert.entity.focal_points.filter(is_active=True)
            cc = [point.email for point in points_focaux]
            context = {
                'alert_name': alert.get_alert_type_display(),
                'site_name': alert.platform.url,
                'points_focaux': [
                    {
                        'name': point.full_name,
                        'email': point.email,
                        'phone': point.phone_number[0] if point.phone_number else None
                    }
                    for point in points_focaux
                ]
            }
        
            
            html_content = render_to_string(
                'template_alerte_analyste.html',
                context
            )
            subject = f"Oju Alert - {alert.get_alert_type_display()} - {alert.platform.url}"
            if self.can_receiveAlert:
                
                send_email_task.delay(
                    subject=subject,
                    body=html_content,
                    to_recipients=[self.notification_email],
                    is_html=True
                )
                
                logger.info(f"Email task queued for alert {alert.id}")
            
            
            requestors = [point.email for point in points_focaux]
            
            create_rtir_ticket.delay(
                subject=subject,
                content=escape(alert.details).replace('\n', '<br>'),
                requestors=requestors,
                admin_cc=[self.notification_email],
                cc= cc,
                priority="High" if alert.alert_type in ['availability', 'ssl', 'domain_unvailable', 'vt'] else "Normal",
                domain=alert.platform.domain.name if alert.platform.domain else None,
                reporter_type="oju",
                status="new"
            )
            
            logger.info(f"RTIR ticket task queued for alert {alert.id}")
            
        except Exception as e:
            logger.error(f"Error sending alert notification for alert {alert.id}: {str(e)}")
            raise