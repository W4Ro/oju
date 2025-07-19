from django.db import models
from django.core.validators import EmailValidator, MinValueValidator, MaxValueValidator
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.contrib.postgres.fields import ArrayField
import json

class Configuration(models.Model):
    PROXY_SCHEMES = [
        ('http', 'HTTP'),
        ('https', 'HTTPS'),
        ('socks4', 'SOCKS4'),
        ('socks5', 'SOCKS5'),
    ]

    email = models.EmailField(
        validators=[EmailValidator()],
        help_text="Email address for receiving alerts"
    )
    
    proxy = ArrayField(
        models.URLField(max_length=255),
        blank=True,
        default=list,
        help_text="List of Proxy URL (scheme://[username:password@]domain:port)"
    )
    
    dns_server = ArrayField(
        models.GenericIPAddressField(),
        blank=True,
        default=list,
        help_text="List of dns server address IP addresses used for domain resolution"
    )

    use_proxy = models.BooleanField(
        default=False,
        help_text="Whether to use the proxy for requests"
    )
    
    use_host_on_proxy_fail = models.BooleanField(
        default=True,
        help_text="Whether to use direct connection if proxy fails"
    )
    
    scan_frequency = models.IntegerField(
        validators=[MinValueValidator(120)],
        help_text="Scan frequency in seconds (minimum 2 minutes)"
    )
    
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp"
    )
    
    user_agent = models.CharField(
        max_length=255,
        unique=True,
        help_text="User Agent that will be used during scans",
        default='Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0'
    )

    max_worker = models.IntegerField(
        default=5,
        validators=[MinValueValidator(5), MaxValueValidator(30)],
        help_text="Maximum simultanous workers"
    )

    receive_alert = models.BooleanField(
        default=False,
        help_text="This is use to know if alert can be sent to email"
    )

    class Meta:
        db_table = 'configuration'
        verbose_name = 'configuration'
        verbose_name_plural = 'configurations'

    
    
    def clean(self):
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=self.scan_frequency,
            period=IntervalSchedule.SECONDS,
        )
        
        task_name = 'Monitoring'
        task_defaults = {
            'interval': schedule,
            'name': task_name,
            'task': 'apps.cerb_scans.tasks.run_monitoring',
            'kwargs': json.dumps({}),
            'enabled': True,
        }
        
        task, _ = PeriodicTask.objects.update_or_create(
            name=task_name,
            defaults=task_defaults
        )
        if _:
            task.interval = schedule
            task.save()