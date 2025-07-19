from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import (
    Scan, SSLScanCriteria, DomainScanCriteria, DefacementScanCriteria,
    WhitelistedDomain, WebsiteScanCriteria
)


class ScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scan
        fields = ['name', 'code', 'description', 'is_active', 'updated_at']
        read_only_fields = [ 'updated_at']


class SSLScanCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SSLScanCriteria
        fields = [ 'scan', 'check_ssl_error', 'check_ssl_expiry']
        read_only_fields = [ 'scan']


class DomainScanCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomainScanCriteria
        fields = [
             'scan', 'check_whois', 'check_dns_servers',
             'check_domain_expiry_error'
        ]
        read_only_fields = [ 'scan']


class WhitelistedDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhitelistedDomain
        fields = [ 'defacement_criteria', 'domain']


class DefacementScanCriteriaSerializer(serializers.ModelSerializer):
    whitelisted_domains = WhitelistedDomainSerializer(many=True, read_only=True)
    
    class Meta:
        model = DefacementScanCriteria
        fields = [
             'scan', 'acceptance_rate', 'whitelisted_domains'
        ]
        read_only_fields = [ 'scan']

class WebsiteScanCriteriaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = WebsiteScanCriteria
        fields = [
             'scan',
            'max_response_time_ms'
        ]
        read_only_fields = [ 'scan']


class UpdateMaxResponseTimeSerializer(serializers.Serializer):
    """
    Serializer for updating the maximum response time.
    """
    max_response_time_ms = serializers.IntegerField(
        min_value=1000,
        max_value=60000,
        help_text="Maximum acceptable response time in ms"
    )


class DefacementScanCriteriaUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating all defacement scan criteria at once.
    """
    acceptance_rate = serializers.IntegerField(
        min_value=0,
        max_value=5000,
        help_text="Acceptance rate between 0 and 5000"
    )
    
    
    whitelisted_domains = serializers.ListField(
        child=serializers.CharField(
            max_length=70,
            validators=[
                RegexValidator(
                    regex=r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$',
                    message="Enter a valid domain name"
                )
            ]
        ),
        help_text="List of domains to whitelist",
        required=False,
        default=[]
    )