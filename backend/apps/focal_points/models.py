import uuid
from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.contrib.postgres.fields import ArrayField

class FocalFunction(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the focal function"
    )
    
    name = models.CharField(
        max_length=255,
        help_text="Name of the focal function"
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
        db_table = 'focal_functions'
        ordering = ['name']
        verbose_name = 'Focal Function'
        verbose_name_plural = 'Focal Functions'

    def __str__(self):
        return self.name

class FocalPoint(models.Model):
    
    phone_regex = RegexValidator(
        regex= r'^\+?1?[\d\s]{9,20}$',
        message="Phone number must be in format: '+999999999'. Up to 15 digits allowed."
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the focal point"
    )
    
    full_name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Full name of the focal point"
    )
    
    phone_number = ArrayField(
        models.CharField(max_length=16, validators=[phone_regex]),
        blank=True,
        default=list,
        help_text="List of phone numbers with country code"
    )
    
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text="Email address"
    )
    
    function = models.ForeignKey(
        FocalFunction,
        on_delete=models.PROTECT,
        related_name='focal_points',
        help_text="Associated function"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether this focal point is active"
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
        db_table = 'focal_points'
        ordering = ['function', 'full_name']
        verbose_name = 'Focal Point'
        verbose_name_plural = 'Focal Points'
        indexes = [
            models.Index(fields=['full_name']), 
            models.Index(fields=['function', 'full_name']), 
        ]

    def __str__(self):
        return f"{self.full_name} ({self.function.name})"

    def clean(self):
        
            
       
        if self.email:
            self.email = self.email.strip()
        
        if self.full_name:
            self.full_name = self.full_name.strip()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)