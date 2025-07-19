from django.core.management.base import BaseCommand
from django.db import transaction
from ...models import (
    Scan, SSLScanCriteria, DomainScanCriteria, DefacementScanCriteria,
    WhitelistedDomain, WebsiteScanCriteria
)


class Command(BaseCommand):
    help = 'Initialize the database with default scan types and their criteria'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting initialization of scan types and criteria...'))
        
        try:
            with transaction.atomic():
                self._create_ssl_scan()
                self._create_domain_scan()
                self._create_defacement_scan()
                self._create_website_scan()
                
                self.stdout.write(self.style.SUCCESS('Successfully initialized all scan types and criteria!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during initialization: {str(e)}'))
    
    def _create_ssl_scan(self):
        """Create SSL Scan and its criteria"""
        self.stdout.write('Creating SSL Scan...')
        
        ssl_scan, created = Scan.objects.get_or_create(
            code='ssl',
            defaults={
                'name': 'SSL Scan',
                'description': 'Scan for SSL certificate issues and expiration',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created SSL Scan'))
        else:
            self.stdout.write('SSL Scan already exists')
        
        SSLScanCriteria.objects.get_or_create(
            scan=ssl_scan,
            defaults={
                'check_ssl_error': True,
                'check_ssl_expiry': True
            }
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully created SSL Scan criteria'))
    
    def _create_domain_scan(self):
        """Create Domain Availability Scan and its criteria"""
        self.stdout.write('Creating Domain Availability Scan...')
        
        domain_scan, created = Scan.objects.get_or_create(
            code='domain',
            defaults={
                'name': 'Domain Availability Scan',
                'description': 'Scan for domain availability and related issues',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created Domain Availability Scan'))
        else:
            self.stdout.write('Domain Availability Scan already exists')
        
        DomainScanCriteria.objects.get_or_create(
            scan=domain_scan,
            defaults={
                'check_whois': True,
                'check_dns_servers': True,
                'check_domain_expiry_error': True
            }
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully created Domain Availability Scan criteria'))
    
    def _create_defacement_scan(self):
        """Create Defacement Checking Scan and its criteria"""
        self.stdout.write('Creating Defacement Checking Scan...')
        
        defacement_scan, created = Scan.objects.get_or_create(
            code='defacement',
            defaults={
                'name': 'Defacement Checking',
                'description': 'Scan for website defacement',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created Defacement Checking Scan'))
        else:
            self.stdout.write('Defacement Checking Scan already exists')
        
        defacement_criteria, _ = DefacementScanCriteria.objects.get_or_create(
            scan=defacement_scan,
            defaults={
                'acceptance_rate': 100
            }
        )
        
        
        default_whitelisted_domains = ['google-analytics.com',
                                        'googletagmanager.com',
                                        'google.com',
                                        'googleapis.com'
                                        ]
        for domain in default_whitelisted_domains:
            WhitelistedDomain.objects.get_or_create(
                defacement_criteria=defacement_criteria,
                domain=domain
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully created Defacement Checking Scan criteria'))
    
    def _create_website_scan(self):
        """Create Website Availability Checking Scan and its criteria"""
        self.stdout.write('Creating Website Availability Checking Scan...')
        
        website_scan, created = Scan.objects.get_or_create(
            code='website',
            defaults={
                'name': 'Website Availability Checking',
                'description': 'Scan for website availability and performance',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created Website Availability Checking Scan'))
        else:
            self.stdout.write('Website Availability Checking Scan already exists')
        
        website_criteria, _ = WebsiteScanCriteria.objects.get_or_create(
            scan=website_scan,
            defaults={
                'max_response_time_ms': 5000,
            }
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully created Website Availability Checking Scan criteria'))