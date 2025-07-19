from django.db import models
import uuid
from apps.entities.models import Entity, Platform

class Alert(models.Model):
    ALERT_TYPES = (
        ('ssl', 'SSL Problem'),
        ('ssl_expiredSoon', 'SSL Certificate expires soon'),
        ('domain_unvailable', 'Domain availability issue'),
        ('domain_expiredSoon', 'The domain expires soon'),
        ('defacement', 'Defacement'),
        ('availability', 'Availability problem'),
        ('vt', 'Flaged on VirusTotal'),
        ('other', 'Other'),
    )

    STATUS_CHOICES = (
        ('new', 'New'),
        ('in_progress', 'In progress'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False positive'),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier of the alert"
    )

    date = models.DateTimeField(
        auto_now_add=True,
        help_text="Alert creation date"
    )

    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='alerts',
        help_text="Entity concerned by the alert"
    )

    platform = models.ForeignKey(
        Platform,
        on_delete=models.CASCADE,
        related_name='alerts',
        help_text="Platform concerned by the alert"
    )

    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPES,
        help_text="Alert Type"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        help_text="Current alert status"
    )

    details = models.TextField(
        help_text="Alert details"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Alert creation date"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modified date"
    )
    
    templates = models.TextField(
        help_text="Content of the email that will be sent to the focal points",
        blank=True,
        null=True
    )
    class Meta:
        db_table = 'alerts'
        ordering = ['-date']
        verbose_name = 'Alerte'
        verbose_name_plural = 'Alertes'

    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.entity.name} - {self.date.strftime('%Y-%m-%d %H:%M')}"
