from rest_framework import serializers
from .models import Configuration
from rest_framework.exceptions import ValidationError
import ipaddress
import concurrent.futures
import re
import dns.resolver
from urllib.parse import urlparse
import requests
from core.common_function import *

class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuration
        fields = ['email', 'proxy', 'user_agent', 'dns_server', 'max_worker', 'use_proxy', 'use_host_on_proxy_fail',
                 'scan_frequency', 'receive_alert', 'last_updated']
        read_only_fields = ['last_updated']

    def validate_scan_frequency(self, value):
        """Validate scan frequency"""
        if value < 120: 
            raise serializers.ValidationError(
                "Scan frequency must be at least 2 minutes (120 seconds)"
            )
        return value
    
    def test_dns(self, dns_ip):
            
        try:
            ipaddress.ip_address(dns_ip)
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [dns_ip]
            resolver.timeout = 2
            resolver.resolve("google.com", 'A')
        except Exception as e:
            return False
        
        return True


    def validate_dns_server(self, value):
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(value)) as executor:
            future_to_dns = {executor.submit(self.test_dns, dns_ip): dns_ip for dns_ip in value}
            for future in concurrent.futures.as_completed(future_to_dns):
                dns_ip = future_to_dns[future]
                try:
                    if not future.result():
                        raise ValidationError(f"The DNS server {dns_ip} doesn't work")
                except Exception as e:
                    raise ValidationError(f"Error while checking DNS Server {dns_ip} ")
        return value
    

    def validate_email(self, value):
        return value.strip()

    def validate_max_worker(self, value):
        if not 5 < value <=30:
            raise serializers.ValidationError(
                "max worker must be less than 10 or great than 5"
            )
        return value

    def check_proxy_url(self, value):
        """Validate proxy URL format and scheme"""
        PROXY_SCHEMES = [
        ('http', 'HTTP'),
        ('https', 'HTTPS'),
        ('socks4', 'SOCKS4'),
        ('socks5', 'SOCKS5'),
    ]
        for _ in value:  
            try:
                parsed = urlparse(_)
                if parsed.scheme not in [scheme for scheme, __ in PROXY_SCHEMES]:
                    raise ValidationError(f"Invalid proxy scheme for {_}")
                    
                
                if parsed.username or parsed.password:
                    if not (parsed.username and parsed.password):
                        raise ValidationError(f"Both username and password must be provided if using authentication: {_}")
                        
                
                if not parsed.netloc:
                    raise ValidationError(f"Invalid proxy domain: {_}")
                if not re.match(r'^[^:]+:\d+$', parsed.netloc.split('@')[-1]):
                    raise ValidationError(f"Invalid proxy port: {_}")
                    
                return True
            except Exception as e:
                raise ValidationError(f"Invalid proxy URL {_} format: {str_exception(e)}")


    def test_single_proxy(self, proxy):
        try:
            proxies = {
                'http': proxy,
                'https': proxy
            }
            response = requests.get('https://www.google.com', proxies=proxies, timeout=5)
            return response.status_code == 200
        except Exception as e:
            return False

    def test_proxy_connection(self, value):
        """Test if proxys are working"""
 
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(value)) as executor:
            future_to_proxy = {executor.submit(self.test_single_proxy, proxy): proxy for proxy in value}
            for future in concurrent.futures.as_completed(future_to_proxy):
                try:
                    if not future.result():
                        raise ValidationError(f"Proxy connection test failed for {future_to_proxy[future]} ")
                except Exception:
                    raise ValidationError(f"Error while testing {future_to_proxy[future]} ")

        return True


    def validate(self, data):
        """Validate proxy connection if use_proxy is True"""
        instance = self.instance
        use_proxy = data.get('use_proxy', instance.use_proxy if instance else False)
        proxies = data.get('proxy', instance.proxy if instance else None)
        
        if use_proxy:
            
            if not proxies:
                raise serializers.ValidationError("Proxy configuration is required when use_proxy is enabled")
            if not (1 <= len(proxies) <= 5):
                raise serializers.ValidationError("You must set between 1 and 5 proxies if use_proxy is enabled.")
            try:
                self.check_proxy_url(proxies)
                self.test_proxy_connection(proxies)
            except ValidationError as e:
                raise serializers.ValidationError(f"Proxy validation failed: {str(e)}")
                    
        dns_server = data.get('dns_server', instance.dns_server if instance else None)
        if 'dns_server' in data:
            if not (1 <= len(dns_server) <= 5):
                raise serializers.ValidationError("You must set between 1 and 5 DNS servers.")
        return data