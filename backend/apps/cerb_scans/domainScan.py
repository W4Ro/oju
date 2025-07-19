import whois
import dns.resolver
import tldextract
from datetime import datetime
from typing import Union, List
import time
from core.definitions import *
from django.core.cache import cache
import logging


logger = logging.getLogger(__name__)

class DNSResolutionError(Exception):
    """Custom exception for DNS resolution errors."""
    def __init__(self, domain: str, errors: Union[str, List[str]]):
        self.domain = domain
        self.errors = [errors] if isinstance(errors, str) else errors
        super().__init__(f"DNS Resolution Errors for {domain}: {', '.join(self.errors)}")

    def to_dict(self):
        return {self.domain: self.errors}

class DomainExpirationError(Exception):
    """Custom exception for domain expiration errors."""
    def __init__(self, domain: str, error: str, day_remaining: int):
        self.domain = domain
        self.error = error
        self.day_remaining = day_remaining
        super().__init__(f"Domain Expiration Error for {domain}: {error}")

    def to_dict(self):
        return {"domain": self.domain, "error": self.error, "day_remaining": self.day_remaining}

class WhoisVerificationError(Exception):
    """Custom exception for Whois verification failures."""
    def __init__(self, domain: str):
        self.domain = domain
        super().__init__(f"Whois verification failed for {domain}")

class DNSServerError(Exception):
    """Custom exception for DNS server-specific failures."""
    def __init__(self, domain: str, server: str, error: str):
        self.domain = domain
        self.server = server
        self.error = error
        super().__init__(f"DNS Server {server} failed for {domain}: {error}")
    def _format_error(self):
        """Format the error message for better readability."""
        return f"DNS Server {self.server} failed for {self.domain}: {self.error}"
    def __str__(self):
        """Return the formatted error message."""
        return f"DNS Server {self.server} failed for {self.domain}. Error: {self.error}"

class AllDNSServersFailedError(Exception):
    """Custom exception when all DNS servers fail."""
    def __init__(self, domain: str, errors: List[str]):
        self.domain = domain
        error_messages = '\n✗ '.join(str(error) for error in errors)
        super().__init__(f"All DNS servers failed to resolve {domain}: \n✗ {error_messages}")

def is_tld(domain: str) -> bool:
    
    extracted = tldextract.extract(domain)
    return extracted.subdomain == ''

def get_dns_server():
    
    dns_server = cache.get(DNS_SERVER_CACHE_KEY)
    if dns_server is None:
        try:
            from apps.config.models import Configuration
            config = Configuration.objects.first()
            if not config:
                logger.error("Error fetching configuration to load dns_server")
                return []
            dns_server = config.dns_server
            cache.set(DNS_SERVER_CACHE_KEY, dns_server, 12 * 60 * 60)
        except Exception as e:
            logger.error("Unexpected exception while fetching dns_server")
            return []
    return dns_server


class DomainChecker:
    DNS_SERVERS = get_dns_server()
    def __init__(self, domain: str, 
                 check_whois: bool = True, 
                 check_dns_server: bool = True, 
                 check_domain_expiry_error: bool = True,
                 timeout: int = 5):
        
        self.domain = domain
        self.timeout = timeout 
        self.check_whois = check_whois
        self.check_dns_server = check_dns_server
        self.check_domain_expiry_error = check_domain_expiry_error

    def resolve_domain(self) -> dict:
        
        try:
            domain_info = whois.whois(self.domain)
            if not domain_info.expiration_date:
                raise WhoisVerificationError(self.domain)
            
            return {
                "expiration_date": domain_info.expiration_date,
            }
        except WhoisVerificationError: 
            raise
        except Exception as e:
            raise DNSResolutionError(self.domain, str(e))

    def resolve_with_dns(self, dns_server: str) -> str:
        
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [dns_server]
            resolver.timeout = self.timeout
            answer = resolver.resolve(self.domain, 'A')
            return answer[0].to_text()
        except Exception as e:
            raise DNSServerError(self.domain, dns_server, str(e))

    def check_expiration(self, expiration_date: Union[datetime, List[datetime]]) -> None:
        
        if not expiration_date:
            pass 

        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]

        days_left = (expiration_date - datetime.now()).days

        if days_left == 7:
            raise DomainExpirationError(
                self.domain, 
                f"CRITICAL: Domain expires in {days_left} days",
                7
            )
        elif days_left == 14:
            raise DomainExpirationError(
                self.domain, 
                f"CRITICAL: Domain expires in {days_left} days",
                14
            )
        elif days_left == 30:
            raise DomainExpirationError(
                self.domain, 
                f"WARNING: Domain expires in {days_left} days",
                30
            )

    def check(self) -> dict:
        
        resolved_ip = None
        
        try:
            if self.check_whois:
                info = self.resolve_domain()
                if self.check_domain_expiry_error and info.get("expiration_date"):
                    self.check_expiration(info["expiration_date"])
        except DomainExpirationError as e:
            raise e
        except (WhoisVerificationError, DNSResolutionError) as e:
            if not self.check_dns_server:
                raise e
            if self.check_dns_server and not self.DNS_SERVERS:
                raise e

        if self.check_dns_server and self.DNS_SERVERS:
            test_fail = True
            dns_errors = []
            for server in self.DNS_SERVERS:
                try:
                    resolved_ip = self.resolve_with_dns(server)
                    test_fail = False
                    break
                except DNSServerError as e:
                    dns_errors.append(e)
                    continue

            if test_fail:
                raise AllDNSServersFailedError(self.domain, dns_errors)

        return {
            "domain": self.domain,
            "resolved_ip": resolved_ip
        }
