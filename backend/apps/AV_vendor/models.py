import uuid
from django.db import models

class AVVendor(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the AV vendor"
    )
    
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the antivirus vendor"
    )
    
    contact = models.CharField(
        max_length=255,
        help_text="Contact information for the vendor"
    )
    
    comments = models.TextField(
        blank=True,
        null=True,
        help_text="Additional comments about the vendor"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation date"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update date"
    )

    class Meta:
        db_table = 'av_vendors'
        ordering = ['name']
        verbose_name = 'AV Vendor'
        verbose_name_plural = 'AV Vendors'

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        
        super().save(*args, **kwargs)