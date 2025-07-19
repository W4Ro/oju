# models.py
from django.db import models
import uuid
from apps.focal_points.models import FocalPoint

class Entity(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier of the entity"
    )
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Entity name"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the entity"
    )
    focal_points = models.ManyToManyField(
        FocalPoint,
        related_name='entities',
        through='EntityFocalPoint',
        help_text="Focal points associated with the entity",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation data"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update date"
    )

    class Meta:
        db_table = 'entities'
        ordering = ['name']
        verbose_name = 'Entity'
        verbose_name_plural = 'Entities'

    def __str__(self):
        return self.name

class EntityFocalPoint(models.Model):
    entity = models.ForeignKey(
        Entity, 
        on_delete = models.CASCADE
    )
    focal_point = models.ForeignKey(
        FocalPoint, 
        on_delete = models.SET_NULL,
        null =True,
        blank=True
    )


class Domain(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique domain identifier"
    )
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Domain name"
    )
    last_scan_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last domain scan date"
    )
    last_ssl_scan_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last SSL Scan Date"
    )
    ssl_issue = models.BooleanField(
        default=False,
        help_text="Indicates if there is an SSL problem"
    )
    domain_issue = models.BooleanField(
        default=False,
        help_text="Indicates if there is a problem with the domain"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Domain IP address"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation date"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modified date"
    )

    class Meta:
        db_table = 'domains'
        ordering = ['name']
        verbose_name = 'Domain'
        verbose_name_plural = 'Domains'

    def __str__(self):
        return self.name


class Platform(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique platform identifier"
    )
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='platforms',
        help_text="Entity owning the platform"
    )
    url = models.URLField(
        unique=True,
        help_text="Platform URL"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Platform status"
    )
    domain = models.ForeignKey(
        Domain,
        on_delete=models.PROTECT,
        related_name='platforms',
        help_text="Domain associated with the platform"
    )
    screenshot = models.TextField(
        null=True,
        blank=True,
        help_text="Screenshot of the platform in base64"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date of creation of the platform"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modification date of the platform"
    )

    class Meta:
        db_table = 'platforms'
        ordering = ['entity']
        verbose_name = 'Platform'
        verbose_name_plural = 'Platforms'

    def __str__(self):
        return f"{self.url} ({self.entity.name})"
    
