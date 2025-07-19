import uuid
from django.db import models
from rest_framework.exceptions import ValidationError
import smtplib
from email.mime.text import MIMEText
import socket
from django.core.validators import EmailValidator, RegexValidator


class MailConfig(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    smtp_server = models.CharField(
        max_length=255,
        help_text="SMTP server address"
    )

    smtp_port = models.IntegerField(
        help_text="SMTP server port"
    )

    use_tls = models.BooleanField(
        default=False,
        help_text="Use TLS encryption"
    )

    use_ssl = models.BooleanField(
        default=False,
        help_text="Use SSL encryption"
    )

    email_host = models.EmailField(
        help_text="Email host address",
        validators=[EmailValidator()]
    )

    email_password = models.CharField(
        max_length=255,
        help_text="Email password"
    )

    default_sender_name = models.CharField(
        max_length=255,
        help_text="Default sender name"
    )

    default_reply_to = models.EmailField(
        null=True,
        blank=True,
        help_text="Default reply-to address (defaults to email_host if not set)"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether this configuration is currently active"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Mail Configuration'
        verbose_name_plural = 'Mail Configurations'

    def clean(self):
        
        if self.use_tls and self.use_ssl:
            raise ValidationError("Cannot use both TLS and SSL simultaneously")

       
        if not 1 <= self.smtp_port <= 65535:
            raise ValidationError("SMTP port must be between 1 and 65535")

        
        if not self.default_reply_to:
            self.default_reply_to = self.email_host

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class EmailLog(models.Model):
    class EmailStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SENT = 'sent', 'Sent'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    subject = models.CharField(
        max_length=255,
        help_text="Email subject"
    )
    
    to_recipients = models.JSONField(
        help_text="List of primary recipients"
    )
    
    cc_recipients = models.JSONField(
        default=list,
        blank=True,
        help_text="List of CC recipients"
    )
    
    bcc_recipients = models.JSONField(
        default=list,
        blank=True,
        help_text="List of BCC recipients"
    )
    
    body = models.TextField(
        help_text="Email body content"
    )
    
    is_html = models.BooleanField(
        default=False,
        help_text="Whether the body content is HTML"
    )
    
    attachments = models.JSONField(
        default=list,
        blank=True,
        help_text="List of attachment information"
    )
    
    status = models.CharField(
        max_length=20,
        choices=EmailStatus.choices,
        default=EmailStatus.PENDING
    )
    
    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Error message if sending failed"
    )
    
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the email was successfully sent"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.status}"
