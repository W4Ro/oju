from django.db import models
import uuid
from apps.users.models import User

class SystemLog(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the logs"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='system_logs',
        help_text="User associated to the log"
    )
    details = models.JSONField(
        help_text="Additionnels details",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Log creation date"
    )

    class Meta:
        ordering = ['-created_at']
        db_table = 'system_logs'
        verbose_name = "Log"
        verbose_name_plural = "Logs"

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"
