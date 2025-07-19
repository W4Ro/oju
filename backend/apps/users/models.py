from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import  EmailValidator
from django.db import models
import uuid
from datetime import datetime
from django.utils import timezone
from apps.roles.models import Role

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not password:
            raise ValueError('Password is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        superuser = self.create_user(email, password, **extra_fields)
        
 
        super_admin_role, created = Role.objects.get_or_create(name="Super Admin")
        superuser.role = super_admin_role
        superuser.save()
        
        return superuser

class User(AbstractBaseUser, PermissionsMixin):
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into admin site"
    )
    is_superuser = models.BooleanField(
        default=False,
        help_text="Designates that this user has all permissions"
    )
    nom_prenom = models.CharField(
        max_length=255,
        help_text="user's first and last name"
    )
    username = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="user's unique name"
    )
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        db_index=True,
        help_text="user's email adress"
    )
    role = models.ForeignKey(
        Role,
        null=True,
        blank= True,
        on_delete=models.PROTECT,
        help_text="User's role"
    )
    is_active = models.BooleanField(
        default=False,
        help_text="User's statut"
    )
    failed_login_attempts = models.IntegerField(
        default=0,
        help_text="Count login attempt failed"
    )
    last_failed_login = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last failed login"
    )
    last_login = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Latest connexion"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="User's creation date"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Latest update date")

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nom_prenom']

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower().strip()
        
        super().save(*args, **kwargs)

class PasswordReset(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        help_text="User requesting reset"
    )
    token = models.CharField(
        max_length=255,
        unique=True,
        help_text="One-time reset token"
    )
    is_used = models.BooleanField(
        default=False,
        help_text="Indicates whether the token has already been used"
    )
    attempts = models.PositiveIntegerField(
        default=0,
        help_text="Number of attempts to use the token"
    )
    expires_at = models.DateTimeField(
        help_text="Token expiration date"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Request creation date"
    )

    class Meta:
        db_table = 'password_resets'
        ordering = ['-created_at']
        verbose_name = 'Password reset'
        verbose_name_plural = 'Password reset'

    def __str__(self):
        return f"Reset token for {self.user.email}"

    @property
    def is_expired(self):
        """Check if token is expired"""
        return datetime.now(self.expires_at.tzinfo) > self.expires_at

    @property
    def is_valid(self):
        """check if token is still valid"""
        return not self.is_used and not self.is_expired and self.attempts < 3

    def increment_attempts(self):
        """Increase tentative attempts"""
        self.attempts += 1
        self.save(update_fields=['attempts'])


class BlacklistedToken(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    token = models.CharField(
        max_length=500,
        help_text="Token JWT revoqued"
    )
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        help_text="User associated with the token"
    )
    blacklisted_at = models.DateTimeField(
        default=timezone.now,
        help_text="Token revocation date"
    )
    reason = models.CharField(
        max_length=100,
        blank=True,
        help_text="Token revocation reason"
    )

    class Meta:
        db_table = 'blacklisted_tokens'
        ordering = ['-blacklisted_at']
        verbose_name = 'Token revoqued'
        verbose_name_plural = 'Tokens revoqued'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'blacklisted_at']),
        ]
        unique_together = ['token', 'user']

    def __str__(self):
        return f"Blacklisted token for {self.user.email}"

    @classmethod
    def is_blacklisted(cls, token):
        """
        check if a token is blacklisted
        """
        return cls.objects.filter(token=token).exists()

    @classmethod
    def clean_expired_tokens(cls, days=7):
        """
        Delete expired blacklisted tokens
        """
        expiry_date = timezone.now() - timezone.timedelta(days=days)
        cls.objects.filter(blacklisted_at__lt=expiry_date).delete()