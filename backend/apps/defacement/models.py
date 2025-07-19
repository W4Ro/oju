from django.db import models
import uuid
from apps.entities.models import Entity, Platform
from rest_framework.exceptions import ValidationError

class Defacement(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier of the defacement"
    )
    
    date = models.DateTimeField(
        auto_now=True,
        help_text="Last scan date"
    )
    
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='defacements',
        help_text="Entity concerned"
    )
    
    platform = models.ForeignKey(
        Platform,
        on_delete=models.CASCADE,
        related_name='defacements',
        help_text="Plateform concerned"
    )
    
    is_defaced = models.BooleanField(
        default=False,
        help_text="Indicates whether the platform is defaced"
    )
    
    normal_state = models.JSONField(
        default=dict,
        help_text="Platform normal state"
    )
    
    last_state = models.JSONField(
        default=dict,
        help_text="Last scanned state"
    )
    
    details = models.TextField(
        blank=True,
        help_text="Last scan details"
    )
    
    normal_state_tree = models.TextField(
        help_text="Normal State Tree"
    )
    
    last_state_tree = models.TextField(
        help_text="Last State Tree"
    )

    class Meta:
        db_table = 'defacements'
        ordering = ['-date']
        verbose_name = 'Défacement'
        verbose_name_plural = 'Défacements'
        indexes = [
            models.Index(fields=['is_defaced']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.platform.url} - {'Defaced' if self.is_defaced else 'Normal'}"


    def clean(self):
        # Validate JSON fields
        if not isinstance(self.normal_state, dict):
            raise ValidationError({'normal_state': 'Must be a valid dictionary'})
        if self.last_state and not isinstance(self.last_state, dict):
            raise ValidationError({'last_state': 'Must be a valid dictionary'})