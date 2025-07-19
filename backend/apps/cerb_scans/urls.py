from django.urls import path
from .views import (
    ScanViewSet, SSLScanCriteriaViewSet, DomainScanCriteriaViewSet,
    DefacementScanCriteriaViewSet, WebsiteScanCriteriaViewSet
)

urlpatterns = [
    path('scans/', ScanViewSet.as_view({
        'get': 'list'
    }), name='list-scan'),
    path('scans/<str:scan_code>/toggle/', ScanViewSet.as_view({
        'post': 'toggle_active'
    }), name='toggle-scan'),
    path('scans/<str:scan_code>/criteria/', ScanViewSet.as_view({
        'get': 'get_criteria'
    }), name='scan-criteria'),

    path('ssl-criteria/toggle-ssl-error/', SSLScanCriteriaViewSet.as_view({
        'post': 'toggle_check_ssl_error'
    }), name='toggle-ssl-error'),
    
    path('ssl-criteria/toggle-ssl-expiry/', SSLScanCriteriaViewSet.as_view({
        'post': 'toggle_check_ssl_expiry'
    }), name='toggle-ssl-expiry'),

    path('domain-criteria/toggle-whois/', DomainScanCriteriaViewSet.as_view({
        'post': 'toggle_check_whois'
    }), name='toggle-whois'),
    
    path('domain-criteria/toggle-dns-servers/', DomainScanCriteriaViewSet.as_view({
        'post': 'toggle_check_dns_servers'
    }), name='toggle-dns-servers'),
    
    path('domain-criteria/toggle-domain-expiry/', DomainScanCriteriaViewSet.as_view({
        'post': 'toggle_check_domain_expiry_error'
    }), name='toggle-domain-expiry'),

    path('defacement-criteria/update/', DefacementScanCriteriaViewSet.as_view({
        'post': 'update_criteria'
    }), name='update-defacement-criteria'),
    
    path('website-criteria/update-max-response-time/', WebsiteScanCriteriaViewSet.as_view({
        'post': 'update_max_response_time'
    }), name='update-max-response-time'),
]