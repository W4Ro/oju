from typing import Dict, List, Optional, Tuple
from requests import Session, exceptions
import warnings
from urllib3.exceptions import InsecureRequestWarning
import socket
import socks

warnings.simplefilter('ignore', InsecureRequestWarning)

class WebsiteCheckerError(Exception):
    """Base exception for all website checker errors."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def to_dict(self) -> Dict:
        """Convert error to dictionary format."""
        return {"error": self.message}

class WebsiteUnavailableError(WebsiteCheckerError):
    """Exception raised when a website is unavailable."""
    def __init__(self, url: str, error: str):
        super().__init__(f"Site unavailable: {url} - {error}")
        self.url = url
        self.error = error

    def to_dict(self) -> Dict:
        return {
            "url": self.url,
            "error": self.error,
            "type": "unavailable"
        }

class WebsiteTimeoutError(WebsiteCheckerError):
    """Exception raised when a request times out."""
    def __init__(self, url: str, timeout: int):
        super().__init__(f"Timeout for {url} after {timeout} seconds")
        self.url = url
        self.timeout = timeout

    def to_dict(self) -> Dict:
        return {
            "url": self.url,
            "timeout": self.timeout,
            "type": "timeout"
        }

class WebsiteSSLError(WebsiteCheckerError):
    """Exception raised when SSL verification fails."""
    def __init__(self, url: str, error: str):
        super().__init__(f"SSL error for {url}: {error}")
        self.url = url
        self.error = error

    def to_dict(self) -> Dict:
        return {
            "url": self.url,
            "ssl_error": self.error,
            "type": "ssl"
        }

class WebsiteHttpError(WebsiteCheckerError):
    """Exception raised when website returns 4xx or 5xx status code."""
    def __init__(self, url: str, status_code: int):
        super().__init__(f"HTTP {status_code} error for {url}")
        self.url = url
        self.status_code = status_code

    def to_dict(self) -> Dict:
        return {
            "url": self.url,
            "status_code": self.status_code,
            "type": "http_error"
        }

class ProxyError(WebsiteCheckerError):
    """Exception raised when there's an issue with the proxy itself."""
    def __init__(self, proxy: str, error: str):
        super().__init__(f"Proxy error for {proxy}: {error}")
        self.proxy = proxy
        self.error = error

    def to_dict(self) -> Dict:
        return {
            "proxy": self.proxy,
            "error": self.error,
            "type": "proxy_error"
        }

class AllProxiesFailedError(WebsiteCheckerError):
    """Exception raised when all proxies fail."""
    def __init__(self, url: str, proxy_errors: List[Dict[str, str]], website_errors: List[Dict[str, str]]):
        proxy_msg = "; ".join([f"{err['proxy']}: {err['error']}" for err in proxy_errors])
        website_msg = "; ".join([f"{err['proxy']}: {err['error']}" for err in website_errors])
        
        error_msg = f"All proxies failed for {url}.\n"
        if proxy_errors:
            error_msg += f"Proxy-related errors:\n{proxy_msg}\n"
        if website_errors:
            error_msg += f"Website-related errors:\n{website_msg}"
            
        super().__init__(error_msg)
        self.url = url
        self.proxy_errors = proxy_errors
        self.website_errors = website_errors

    def to_dict(self) -> Dict:
        return {
            "url": self.url,
            "proxy_errors": self.proxy_errors,
            "website_errors": self.website_errors,
            "type": "all_proxies_failed",
            "is_proxy_issue": len(self.website_errors) == 0 and len(self.proxy_errors) > 0
        }

class WebsiteChecker:
    """A class to check website availability with proxy support."""
    
    def __init__(
        self,
        proxy_list: Optional[List[str]] = None,
        user_agent: Optional[str] = None,
        timeout: int = 10,
        verify_ssl: bool = True
    ):
        self.proxy_list = proxy_list or []
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.headers = {"User-Agent": user_agent} if user_agent else {}
        self.session = Session()

    def _create_proxy_dict(self, proxy: str) -> Dict[str, str]:
        return {
            'http': proxy,
            'https': proxy
        }

    def _make_request(self, url: str, proxies: Optional[Dict[str, str]] = None, verify: bool = True) -> Dict:
        try:
            response = self.session.get(
                url,
                headers=self.headers,
                proxies=proxies,
                timeout=self.timeout,
                verify=verify
            )

            if not response.ok:
                raise WebsiteHttpError(url, response.status_code)

            return {
                "status": "success",
                "proxy_used": proxies.get('http') if proxies else None,
                "status_code": response.status_code,
                "ssl_verify": verify
            }

        except exceptions.SSLError as ssl_error:
            if verify and not self.verify_ssl:
                return self._make_request(url, proxies, verify=False)
            raise WebsiteSSLError(url, str(ssl_error))

        except exceptions.Timeout:
            raise WebsiteTimeoutError(url, self.timeout)

        except (exceptions.ConnectionError, socket.gaierror) as e:#here I can do socket.getaddrinfo('proxy') to know if the socket.gaierror is because of the proxy 
            raise WebsiteUnavailableError(url, str(e))

        except (exceptions.ProxyError, socks.ProxyConnectionError, socks.GeneralProxyError) as e:
            if proxies:
                raise ProxyError(proxies['http'], str(e))
            raise

        except Exception as e:
            raise WebsiteCheckerError(f"Unexpected error: {str(e)}")

    def check(self, url: str) -> Dict:
        if not self.proxy_list:
            return self._make_request(url)

        proxy_errors = []
        website_errors = []

        for proxy in self.proxy_list:
            try:
                proxies = self._create_proxy_dict(proxy)
                return self._make_request(url, proxies)

            except ProxyError as e:
                proxy_errors.append({
                    "proxy": proxy,
                    "error": str(e)
                })
                continue

            except (WebsiteUnavailableError, WebsiteTimeoutError, WebsiteSSLError, WebsiteHttpError) as e:
                website_errors.append({
                    "proxy": proxy,
                    "error": str(e)
                })
                continue

            except WebsiteCheckerError as e:
                website_errors.append({
                    "proxy": proxy,
                    "error": str(e)
                })
                continue

        # If we get here, all proxies have failed
        raise AllProxiesFailedError(url, proxy_errors, website_errors)