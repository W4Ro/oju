from django.core.management.base import BaseCommand
from apps.tools_integrated.models import Integration, RTIR, Cerebrate, VirusTotal

class Command(BaseCommand):
    help = 'Initialize the integration tools'

    def handle(self, *args, **kwargs):
        self.stdout.write('initializing integration tools...')

        integrations_data = [
            {
                'name': 'RTIR',
                'description': """
                Request Tracker for Incident Response (RTIR) is a security incident tracking system
                based on Request Tracker. It helps track, manage, and coordinate responses to security incidents.
                """
            },
            {
                'name': 'Cerebrate',
                'description': """
                Cerebrate is a management tool for security information sharing communities.
                It allows organizations to manage users, share information, and synchronize across different platforms.
                """
            },
            {
                'name': 'VirusTotal',
                'description': """
                VirusTotal is a service that analyzes suspicious files and URLs to detect malware types
                identified by antivirus engines and website scanners. It automates reputation checks and threat analysis.
                """
            } 
        ]

        for data in integrations_data:
            Integration.objects.get_or_create(
                name=data['name'],
                defaults={'description': data['description']}
            )
            self.stdout.write(self.style.SUCCESS(f'{data["name"]} integration created'))

        if not RTIR.objects.exists():
            RTIR.objects.create(
                url='https://rtir.example.com',
                username='admin',
                password='password',
                is_active=False
            )
            self.stdout.write(self.style.SUCCESS('RTIR configuration created'))
        else:
            self.stdout.write(self.style.WARNING('RTIR configuration already exists'))

        if not Cerebrate.objects.exists():
            Cerebrate.objects.create(
                url='https://cerebrate.example.com',
                api_key='default-api-key',
                is_active=False,
                refresh_frequency=604800
            )
            self.stdout.write(self.style.SUCCESS('Ceregrate configuration created'))
        else:
            self.stdout.write(self.style.WARNING('Cerebrate configuration already exists'))

        

        if not VirusTotal.objects.exists():
            VirusTotal.objects.create(
                api_key='default-api-key',
                scan_frequency=604800,
                is_active=False,
            )
            self.stdout.write(self.style.SUCCESS('Configuration VirusTotal created'))
        else:
            self.stdout.write(self.style.WARNING('Configuration VirusTotal already exists'))

        self.stdout.write(self.style.SUCCESS('Initialisation finished successfully'))

        