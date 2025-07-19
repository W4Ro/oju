from django.db import models
from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json

class Integration(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Tool name"
    )
    description = models.TextField(
        help_text="Tool description"
    )

    class Meta:
        db_table = 'integrations'
        ordering = ['name']

    def __str__(self):
        return self.name

class RTIR(models.Model):
    url = models.URLField(help_text="RTIR server URL")
    username = models.CharField(
        max_length=255,
        help_text="username used for authentication"
    )
    password = models.CharField(
        max_length=255,
        help_text="password used for authentication"
    )
    is_active = models.BooleanField(
        default=False,
        help_text="whether this tool is active"
        )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update date"
    )

    class Meta:
        db_table = 'rtir_config'
        verbose_name = 'RTIR Configuration'
        verbose_name_plural = 'RTIR Configuration'

    def __str__(self):
        return f"RTIR Configuration - {self.url}"

    def save(self, *args, **kwargs):
        if not self.pk and RTIR.objects.exists():
            raise ValueError("An RTIR configuration already exists")
        super().save(*args, **kwargs)

class Cerebrate(models.Model):
    FREQUENCY_CHOICES = (
        (86400, '1 Jour'),
        (172800, '2 Jours'),
        (259200, '3 Jours'),
        (345600, '4 Jours'),
        (432000, '5 Jours'),
        (518400, '6 Jours'),
        (604800, '7 Jours')
    )

    url = models.URLField(help_text="Cerebrate Server URL")
    api_key = models.CharField(
        max_length=255,
        help_text="api_key for cerebrate using"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="whether this tool is active"
    )
    refresh_frequency = models.IntegerField(
        choices=FREQUENCY_CHOICES,
        default=604800,
        help_text="Refresh rate in seconds"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update date"
    )

    class Meta:
        db_table = 'cerebrate_config'
        verbose_name = 'Cerebrate Configuration'
        verbose_name_plural = 'Cerebrate Configuration'

    def __str__(self):
        return f"Cerebrate Configuration - {self.url}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        if is_new and Cerebrate.objects.exists():
            raise ValueError("A Cerebrate configuration already exists")

        super().save(*args, **kwargs)

       
        self._update_periodic_task()

    def _update_periodic_task(self):
        """Updates or creates the recurring task."""

        task_name = 'cerebrate-refresh-task'
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=self.refresh_frequency,
            period = IntervalSchedule.SECONDS,
        )

        task, _ = PeriodicTask.objects.update_or_create(
            name=task_name,
            defaults={
                'task': 'apps.tools_integrated.tasks.refresh_cerebrate',
                'interval': schedule,
                'enabled': self.is_active,
                'kwargs': json.dumps({}),
            }
        )

        if _:
            task.interval = schedule
            task.enabled = self.is_active
            task.save()

class VirusTotal(models.Model):
    FREQUENCY_CHOICES = (
        (86400, '1 Jour'),
        (172800, '2 Jours'),
        (259200, '3 Jours'),
        (345600, '4 Jours'),
        (432000, '5 Jours'),
        (518400, '6 Jours'),
        (604800, '7 Jours')
    )

    api_key = models.CharField(
        max_length=255,
        help_text="api_key for virustotal using"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="whether this tool is active"
    )
    scan_frequency = models.IntegerField(
        choices=FREQUENCY_CHOICES,
        default=604800,
        help_text="scan frequency in seconds"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update date"
    )

    class Meta:
        db_table = 'virustotal_config'
        verbose_name = 'virustotal Configuration'
        verbose_name_plural = 'VirusTotal Configuration'

    def __str__(self):
        return f"virustotal Configuration - {self.url}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        if is_new and VirusTotal.objects.exists():
            raise ValueError("An VirusTotal configuration already exists")

        super().save(*args, **kwargs)

       
        self._update_periodic_task()

    def _update_periodic_task(self):
        """Updates or creates the recurring task."""

        task_name = 'virustotal-scan-task'
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=self.scan_frequency,
            period = IntervalSchedule.SECONDS,
        )

        task, _ = PeriodicTask.objects.update_or_create(
            name=task_name,
            defaults={
                'task': 'apps.tools_integrated.tasks.virustotal_scan',
                'interval': schedule,
                'enabled': self.is_active,
                'kwargs': json.dumps({}),
            }
        )

        if _:
            task.interval = schedule
            task.enabled = self.is_active
            task.save()