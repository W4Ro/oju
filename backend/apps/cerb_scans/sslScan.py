from typing import Dict, List, Optional, Union, Any, Tuple
from urllib.parse import urlparse
import socket
import ssl
from datetime import datetime, timedelta
import socks
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID

class SSLCheckerError(Exception):
    """Base exception for all SSL checker errors."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def to_dict(self) -> Dict:
        """Convert error to dictionary format."""
        return {"error": self.message}

class ConnectionError(SSLCheckerError):
    """Exception for connection-related issues (timeout, unreachable, etc.)"""
    def __init__(self, hostname: str, reason: str):
        self.hostname = hostname
        self.reason = reason
        super().__init__(f"Connection failed to {hostname}: {reason}")

    def to_dict(self) -> Dict:
        return {
            "type": "connection_error",
            "hostname": self.hostname,
            "reason": self.reason
        }

class CertificateError(SSLCheckerError):
    """Exception for certificate-related issues (expired, invalid, etc.)"""
    def __init__(self, hostname: str, errors: List[str]):
        self.hostname = hostname
        self.errors = errors
        super().__init__(f"Certificate validation failed for {hostname}: {', '.join(errors)}")

    def to_dict(self) -> Dict:
        return {
            "type": "certificate_error",
            "hostname": self.hostname,
            "errors": self.errors
        }

class SSLHandshakeError(CertificateError):
    """Exception spécifique pour les timeouts durant le handshake SSL."""
    def __init__(self, hostname: str):
        self.hostname = hostname
        super().__init__(
            hostname, 
            [f"SSL handshake operation Error for{hostname} "]
        )

    def to_dict(self) -> Dict:
        return {
            "type": "ssl_handshake_timeout",
            "hostname": self.hostname,
            "errors": self.errors
        }

class ProxyError(SSLCheckerError):
    """Exception for proxy-related issues"""
    def __init__(self, proxy_url: str, reason: str):
        self.proxy_url = proxy_url
        self.reason = reason
        super().__init__(f"Proxy error with {proxy_url}: {reason}")

    def to_dict(self) -> Dict:
        return {
            "type": "proxy_error",
            "proxy_url": self.proxy_url,
            "reason": self.reason
        }

class AllProxiesFailedError(SSLCheckerError):
    """Exception raised when all proxies fail."""
    def __init__(self, hostname: str, proxy_errors: List[Dict], site_errors: List[Dict]):
        proxy_msg = "; ".join([f"{err['proxy_url']}: {err['reason']}" for err in proxy_errors])
        site_msg = "; ".join([f"via {err['proxy_url']}: {err['reason']}" for err in site_errors])
        
        error_msg = f"All proxies failed for {hostname}.\n"
        if proxy_errors:
            error_msg += f"Proxy-related errors:\n{proxy_msg}\n"
        if site_errors:
            error_msg += f"Site-related errors:\n{site_msg}\n "
            
        super().__init__(error_msg)
        self.hostname = hostname
        self.proxy_errors = proxy_errors
        self.site_errors = site_errors

    def to_dict(self) -> Dict:
        return {
            "type": "all_proxies_failed",
            "hostname": self.hostname,
            "proxy_errors": self.proxy_errors,
            "site_errors": self.site_errors,
            "is_proxy_issue": len(self.site_errors) == 0 and len(self.proxy_errors) > 0
        }

class CertificateExpirationWarning(SSLCheckerError):
    """Custom exception for certificate expiration warnings."""
    def __init__(self, hostname: str, level: str, days_remaining: int):
        self.hostname = hostname
        self.level = level
        self.days_remaining = days_remaining
        message = f"{level.upper()}: Certificate for {hostname} expires in {days_remaining} days"
        super().__init__(message)
    
    def to_dict(self) -> Dict:
        return {
            "type": "expiration_warning",
            "domain": self.hostname, 
            "level": self.level, 
            "days_remaining": self.days_remaining,
            "message": self.message
        }

class CertificateInfo:
    """Container for parsed certificate information."""
    
    def __init__(self, cert: x509.Certificate):
        self.cert = cert
        self._parse_certificate()

    def _parse_certificate(self) -> None:
        """Extract and parse relevant certificate information."""
        self.subject = self._get_name_attribute(self.cert.subject, NameOID.COMMON_NAME)
        self.issuer = self._get_name_attribute(self.cert.issuer, NameOID.COMMON_NAME)
        self.valid_from = self.cert.not_valid_before_utc
        self.valid_until = self.cert.not_valid_after_utc
        self.serial_number = self.cert.serial_number

    @staticmethod
    def _get_name_attribute(name: x509.Name, oid: x509.ObjectIdentifier) -> str:
        try:
            return name.get_attributes_for_oid(oid)[0].value
        except IndexError:
            return None

class SSLChecker:
    """A comprehensive utility class for performing SSL certificate checks."""

    WARNING_THRESHOLDS = {
        'critical': timedelta(days=7),
        'warning': timedelta(days=14),
        'notice': timedelta(days=30)
    }

    def __init__(
        self,
        hostname: str,
        port: int = 443,
        proxy_urls: Optional[List[str]] = None,
        timeout: int = 10,
        check_ssl_error: bool = True,
        check_ssl_expiry: bool = True
    ):
        self.hostname = hostname
        self.port = port
        self.proxy_urls = proxy_urls if proxy_urls else []
        self.timeout = timeout
        self.cert_info = None
        self.check_ssl_error = check_ssl_error
        self.check_ssl_expiry = check_ssl_expiry
        self.current_proxy_index = 0

    def _create_connection(self) -> socket.socket:
        # If SSL checks are disabled, don't even try to connect
        if not self.check_ssl_error:
            return None
        
        # Direct connection (no proxy)
        if not self.proxy_urls:
            try:
                sock = socket.create_connection(
                    (self.hostname, self.port),
                    timeout=self.timeout
                )
                return sock
            except socket.timeout:
                raise ConnectionError(self.hostname, f"Connection timed out after {self.timeout} seconds")
            except socket.gaierror:
                raise ConnectionError(self.hostname, "DNS resolution failed")
            except Exception as e:
                raise ConnectionError(self.hostname, f"Connection error: {str(e)}")
        
        # Try proxies one by one
        proxy_errors = []
        site_errors = []

        # Start from the current proxy index for optimization
        for i in range(len(self.proxy_urls)):
            proxy_index = (self.current_proxy_index + i) % len(self.proxy_urls)
            proxy_url = self.proxy_urls[proxy_index]
            
            try:
                proxy = urlparse(proxy_url)
                proxy_types = {
                    'socks5': socks.SOCKS5,
                    'socks4': socks.SOCKS4,
                    'http': socks.HTTP,
                    'https': socks.HTTP
                }
                
                if proxy.scheme not in proxy_types:
                    proxy_errors.append({
                        "proxy_url": proxy_url,
                        "reason": f"Unsupported proxy scheme: {proxy.scheme}"
                    })
                    continue

                try:
                    sock = socks.create_connection(
                        (self.hostname, self.port),
                        timeout=self.timeout,
                        proxy_type=proxy_types[proxy.scheme],
                        proxy_addr=proxy.hostname,
                        proxy_port=proxy.port,
                        proxy_username=proxy.username,
                        proxy_password=proxy.password
                    )
                    # Update current proxy index to the successful one for next try
                    self.current_proxy_index = proxy_index
                    return sock
                except socks.ProxyConnectionError as e:
                    proxy_errors.append({
                        "proxy_url": proxy_url,
                        "reason": f"Proxy connection error: {str(e)} \n"
                    })
                except socket.timeout:
                    proxy_errors.append({
                        "proxy_url": proxy_url,
                        "reason": f"Connection timed out after {self.timeout} seconds \n"
                    })
                except socket.gaierror:
                    # DNS resolution failed - could be a site issue via this proxy
                    site_errors.append({
                        "proxy_url": proxy_url,
                        "reason": "DNS resolution failed \n"
                    })
                except Exception as e:
                    proxy_errors.append({
                        "proxy_url": proxy_url,
                        "reason": f"Proxy error: {str(e)} \n"
                    })
            
            except Exception as e:
                proxy_errors.append({
                    "proxy_url": proxy_url,
                    "reason": f"Proxy URL parsing error: {str(e)} \n"
                })
        
        # If we've tried all proxies and none worked
        if proxy_errors or site_errors:
            raise AllProxiesFailedError(self.hostname, proxy_errors, site_errors)
        else:
            raise ConnectionError(self.hostname, "No valid proxies available")

    def get_certificate(self) -> None:
        try:
            context = ssl.create_default_context()
            with self._create_connection() as sock:
                if sock is None:  # SSL checks disabled
                    return
                    
                with context.wrap_socket(sock, server_hostname=self.hostname) as ssock:
                    der_cert = ssock.getpeercert(binary_form=True)
                    cert = x509.load_der_x509_certificate(der_cert, default_backend())
                    self.cert_info = CertificateInfo(cert)
        except (ConnectionError, ProxyError, AllProxiesFailedError):
            raise
        except ssl.SSLError as e:
            raise CertificateError(self.hostname, [f"SSL Error: {str(e)}"])
        except Exception as e:
            raise SSLHandshakeError(self.hostname, [f"Certificate retrieval failed: {str(e)}"])

    def check_expiry(self) -> None:
        if not self.check_ssl_expiry or not self.check_ssl_error or not self.cert_info:
            return
            
        now = datetime.now().replace(tzinfo=self.cert_info.valid_until.tzinfo)
        
        if now < self.cert_info.valid_from:
            raise CertificateError(
                self.hostname,
                ["Certificate is not yet valid"]
            )
            
        if now > self.cert_info.valid_until:
            raise CertificateError(
                self.hostname,
                ["Certificate has expired"]
            )

    def check_expiry_warning(self) -> None:
        if not self.check_ssl_expiry or not self.check_ssl_error or not self.cert_info:
            return
        
        now = datetime.now().replace(tzinfo=self.cert_info.valid_until.tzinfo)
        time_remaining = self.cert_info.valid_until - now
        
        for level, threshold in self.WARNING_THRESHOLDS.items():
            if time_remaining == threshold:
                raise CertificateExpirationWarning(
                    self.hostname,
                    level=level,
                    days_remaining=time_remaining.days
                )
                # Only raise the highest severity warning
                break

    def get_certificate_info(self) -> Dict[str, Union[str, datetime]]:
        if not self.cert_info:
            return {
                'status': 'No certificate information available',
                'reason': 'SSL checks disabled' if not self.check_ssl_error else 'Unknown error'
            }
        
        return {
            'subject': self.cert_info.subject,
            'issuer': self.cert_info.issuer,
            'valid_from': self.cert_info.valid_from,
            'valid_until': self.cert_info.valid_until,
            'serial_number': hex(self.cert_info.serial_number)[2:].upper()
        }

    def verify_certificate(self) -> Dict[str, Any]:
        # If SSL checks are disabled, return early
        if not self.check_ssl_error:
            return {
                'status': 'skipped',
                'reason': 'SSL checks disabled'
            }
            
        try:
            self.get_certificate()
            
            if self.check_ssl_expiry:
                self.check_expiry()
                self.check_expiry_warning()
                
            return {
                'status': 'valid',
                **self.get_certificate_info()
            }
            
        except CertificateExpirationWarning as warning:
            # Certificate is valid but expires soon
            raise warning
            
        except CertificateError as e:
            # Certificate validation failed
            raise

        except SSLHandshakeError as e:
            raise
            
        except (ConnectionError, ProxyError, AllProxiesFailedError):
            # Re-raise connection or proxy errors
            raise
            
        except Exception as e:
            # Unexpected errors
            raise ConnectionError(self.hostname, f"Unexpected error: {str(e)}")
