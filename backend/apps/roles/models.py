import uuid
from django.db import models
from django.utils import timezone

class Role(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the role"
    )

    description = models.TextField(
        blank=True,
        help_text="Description of the role and its purpose"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether this role is active or not"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'roles'
        ordering = ['name']

class Permission(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    feature_name = models.CharField(
        max_length=255,
        help_text="Name of the feature (e.g., 'agents', 'templates')"
    )

    permission_name = models.CharField(
        max_length=255,
        help_text="Name of the permission (e.g., 'create', 'read', 'update')"
    )

    permission_code = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique code for the permission (e.g., 'agents_create')"
    )

    description = models.TextField(
        blank=True,
        help_text="Detailed description of what this permission allows"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.feature_name} - {self.permission_name}"

    class Meta:
        db_table = 'permissions'
        unique_together = ['feature_name', 'permission_name']
        ordering = ['feature_name', 'permission_name']

class RolePermission(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )

    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'role_permissions'
        unique_together = ['role', 'permission']
        ordering = ['role', 'permission']

    def __str__(self):
        return f"{self.role.name} - {self.permission.permission_code}"