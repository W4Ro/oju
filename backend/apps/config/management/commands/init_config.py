from django.db import transaction
from django.core.management.base import BaseCommand
from ...models import Configuration

config = {
    'email': 'oju@example.com',
    'proxy': ['http://proxy.example.com:8080'],
    'use_proxy': False,
    'use_host_on_proxy_fail': True,
    'scan_frequency': 900,
    'user_agent': "Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0",
    'max_worker': 20,
    'receive_alert': False
    }


class Command(BaseCommand):
    help = 'Initialize configuration with default values'


    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                
                Configuration.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS('Existing configurations deleted')
                )

                Configuration.objects.create(**config)
                self.stdout.write(
                    self.style.SUCCESS(f'Created configuration with email: {config["email"]}')
                )

                self.stdout.write(
                    self.style.SUCCESS('Successfully initialized default configurations')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error initializing configurations: {str(e)}')
            )
            raise
