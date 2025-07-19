from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Alert
from .services import AlertNotificationService
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Alert)
def handle_alert_creation(sender, instance, created, **kwargs):
    """
    Signal that fires after an alert is saved.

    Args:
        sender: The model that sends the signal (Alert)
        instance: The instance of the alert that was just saved
        created: Boolean indicating whether this is a creation or an update
        kwargs: Additional arguments 
    """
    if created:
        try:
            service = AlertNotificationService()
            service.send_alert_notification(instance)
        except Exception as e:
            logger.error(f"Error queuing notification tasks for alert {instance.id}: {str(e)}")

