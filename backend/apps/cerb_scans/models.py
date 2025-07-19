from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Scan(models.Model):
    """
    Main model for different types of security scans.
    """
    SCAN_TYPES = (
        ('ssl', 'SSL Scan'),
        ('domain', 'Domain Availability Scan'),
        ('defacement', 'Defacement Checking'),
        ('website', 'Website Availability Checking'),
    )
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Name of the scan"
    )

    code = models.CharField(
        max_length=50, 
        choices=SCAN_TYPES, 
        unique=True,
        help_text="Scan code"
    )

    description = models.TextField(
        help_text="Description of the scan"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Indicate if the scan is active or not"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Scan creation date"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modified date"
    )
    
    def __str__(self):
        return self.name


class SSLScanCriteria(models.Model):
    """
    Criteria for SSL scan.
    """
    scan = models.OneToOneField(
        Scan, 
        on_delete=models.CASCADE, 
        related_name='ssl_criteria', 
        limit_choices_to={'code': 'ssl'}
    )

    check_ssl_error = models.BooleanField(
        default=True,
        help_text="SSL Error will be checked or not"
    )

    check_ssl_expiry = models.BooleanField(
        default=True,
        help_text="SSL Expiry will be checked"
    )
    
    def __str__(self):
        return f"SSL Scan Criteria for {self.scan.name}"


class DomainScanCriteria(models.Model):
    """
    Criteria for domain availability scan.
    """
    scan = models.OneToOneField(
        Scan, 
        on_delete=models.CASCADE, 
        related_name='domain_criteria',
        limit_choices_to={'code': 'domain'}
    )

    check_whois = models.BooleanField(
        default=True,
        help_text="Indicate if whois will be used during the scan"
    )

    check_dns_servers = models.BooleanField(
        default=True,
        help_text="Indicate if DNS server that are set up will be used during the scan"
    )

    check_domain_expiry_error = models.BooleanField(
        default=True,
        help_text="Indicate if Alert will be raised when expiry date is coming soon"
    )
    
    def __str__(self):
        return f"Domain Scan Criteria for {self.scan.name}"


class DefacementScanCriteria(models.Model):
    """
    Criteria for defacement checking scan.
    """
    scan = models.OneToOneField(
        Scan, 
        on_delete=models.CASCADE, 
        related_name='defacement_criteria',
        limit_choices_to={'code': 'defacement'}
    )

    acceptance_rate = models.IntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(5000)],
        help_text="The acceptance rate value difference between two HTML code lentght"
    )
    
    def __str__(self):
        return f"Defacement Scan Criteria for {self.scan.name}"


class WhitelistedDomain(models.Model):
    """
    Whitelisted domains for defacement scan.
    """
    defacement_criteria = models.ForeignKey(
        DefacementScanCriteria, 
        on_delete=models.CASCADE, 
        related_name='whitelisted_domains'
    )

    domain = models.CharField(
        max_length=50,
        help_text="Domain that will be whitelist during defacement checking"
    )
    
    class Meta:
        unique_together = ('defacement_criteria', 'domain')
    
    def __str__(self):
        return self.domain


class WebsiteScanCriteria(models.Model):
    """
    Criteria for website availability checking scan.
    """
    scan = models.OneToOneField(Scan, 
                                on_delete=models.CASCADE, 
                                related_name='website_criteria',
                               limit_choices_to={'code': 'website'})
    
    max_response_time_ms = models.IntegerField(default=5000, 
                                             help_text="Maximum acceptable response time in ms")
    
    def __str__(self):
        return f"Website Scan Criteria for {self.scan.name}"
