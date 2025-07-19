"""
VirusTotal Scanner Module for analyzing URLs, domains and IP addresses.
All exceptions and the scanner class are defined in this file.
"""
import vt
from datetime import datetime
import json
import asyncio
import logging
import aiohttp
from typing import Dict, Any

import logging
logger = logging.getLogger(__name__)

class ScannerBaseException(Exception):
    """Base exception for all scanner errors."""
    
    def __init__(self, message: str, details: Dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class APIKeyError(ScannerBaseException):
    """Exception raised when API key is invalid or missing."""
    pass

class NetworkError(ScannerBaseException):
    """Exception raised when network connection fails."""
    pass

class RateLimitError(ScannerBaseException):
    """Exception raised when API rate limit is exceeded."""
    pass

class ScanError(ScannerBaseException):
    """Exception raised when scan operation fails."""
    pass

class ResourceNotFoundError(ScannerBaseException):
    """Exception raised when requested resource is not found."""
    pass

class ValidationError(ScannerBaseException):
    """Exception raised when input validation fails."""
    pass

class ConfigurationError(ScannerBaseException):
    """Exception raised when configuration is invalid."""
    pass

class AnalysisError(ScannerBaseException):
    """Exception raised when analysis operation fails."""
    pass

class TimeoutError(ScannerBaseException):
    """Exception raised when operation times out."""
    pass

class AuthenticationError(ScannerBaseException):
    """Exception raised when authentication with API fails."""
    pass

class PermissionError(ScannerBaseException):
    """Exception raised when access to a resource is denied."""
    pass

class ServiceUnavailableError(ScannerBaseException):
    """Exception raised when the VirusTotal service is unavailable."""
    pass

class VirusTotalScanner:
    
    
    def __init__(
        self,
        api_key: str,
        timeout: int = 300
    ):
        """
        Initialize the VirusTotal scanner.
        
        Args:
            api_key: VirusTotal API key
            timeout: Maximum time (in seconds) to wait for scan results
        
        Raises:
            APIKeyError: If the API key is empty or None
        """
        if not api_key:
            raise APIKeyError("VirusTotal API key is required")
        
        self.api_key = api_key
        self.timeout = timeout
        self._client = None
    
    async def _get_client(self) -> vt.Client:
        """
        Get or create a VirusTotal client instance.
        
        Returns:
            An initialized VirusTotal client
            
        Raises:
            APIKeyError: If the API key is invalid
            AuthenticationError: If authentication fails
            NetworkError: If a network error occurs
        """
        if self._client is None:
            try:
                self._client = vt.Client(self.api_key)
            except vt.APIError as e:
                error_msg = str(e).lower()
                error_type = getattr(e, 'code', None) or str(e.__class__.__name__).lower()
                
                if "wrongcredentialserror" in error_type or "wrong api key" in error_msg:
                    raise APIKeyError("Invalid or expired API key")
                if "forbidden" in error_msg:
                    raise PermissionError("Access denied to VirusTotal API")
                if "unauthorized" in error_msg:
                    raise AuthenticationError("Authentication failed with VirusTotal API")
                
                raise NetworkError(f"Error initializing client: {str(e)}")
                
        return self._client
    
    async def close(self) -> None:
        """
        Close the VirusTotal client if it exists.
        
        This method should be called when the scanner is no longer needed
        to properly release network resources.
        """
        if self._client:
            try:
                await self._client.close_async()
                self._client = None
            except RuntimeError as e:
                logger.warning(f"Error closing client: {str(e)}")
        
    async def verify_api_key(self) -> bool:
        """
        Verify if the API key is valid.
        
        Returns:
            bool: True if the API key is valid, False otherwise
            
        Raises:
            APIKeyError: If the API key is invalid
            NetworkError: If a network error occurs
        """
        try:
            client = await self._get_client()
            # Try a simple API call that requires minimal resources
            await client.get_object_async("/ip_addresses/8.8.8.8")
            return True
        except APIKeyError:
            raise
        except Exception as e:
            raise NetworkError(f"Error verifying API key: {str(e)}")

    async def _handle_vt_error(self, error: vt.APIError) -> None:
        """
        Handle VirusTotal API errors and raise appropriate exceptions.
        
        Args:
            error: VirusTotal API error
            
        Raises:
            APIKeyError: If API key is invalid
            ResourceNotFoundError: If requested resource is not found
            RateLimitError: If API rate limit is exceeded
            PermissionError: If access to resource is denied
            AuthenticationError: If authentication fails
            ServiceUnavailableError: If service is temporarily unavailable
            ScanError: For other API errors
        """
        error_msg = str(error).lower()
        error_type = getattr(error, 'code', None) or str(error.__class__.__name__).lower()
        
        # Check for credential errors first
        if "wrongcredentialserror" in error_type or "wrong api key" in error_msg:
            raise APIKeyError("Invalid or expired API key")
        elif "not found" in error_msg:
            raise ResourceNotFoundError("Resource not found")
        elif "quota exceeded" in error_msg or "rate limit" in error_msg:
            raise RateLimitError("API rate limit exceeded")
        elif "forbidden" in error_msg:
            raise PermissionError("Access denied to resource")
        elif "unauthorized" in error_msg:
            raise AuthenticationError("Authentication failed")
        elif "service unavailable" in error_msg or "503" in error_msg:
            raise ServiceUnavailableError("VirusTotal service temporarily unavailable")
        else:
            raise ScanError(f"Error interacting with API: {str(error)}")

    async def scan_url(self, url: str) -> Dict[str, Any]:
        """
        Analyze a URL using VirusTotal.
        
        Args:
            url: URL to analyze
            
        Returns:
            Analysis result dictionary
        """
        
        client = await self._get_client()
        
        try:
            url_obj = await client.scan_url_async(url)
        except vt.APIError as e:
            await self._handle_vt_error(e)
        
        start_time = datetime.now()
        
        while True:
            elapsed_time = (datetime.now() - start_time).total_seconds()
            
            if elapsed_time > self.timeout:
                raise TimeoutError(f"Timeout waiting for scan results after {elapsed_time:.1f}s")
            
            try:
                analysis = await client.get_object_async("/analyses/{}", url_obj.id)
                
                if analysis.status == "completed":
                    result = analysis.to_dict()
                    
                    
                    # Add metadata
                    result["_metadata"] = {
                        "scan_date": datetime.now().isoformat(),
                        "scan_type": "url",
                        "target": url,
                        "elapsed_time": elapsed_time
                    }
                    
                    return result
                elif analysis.status == "failed":
                    raise AnalysisError("Analysis failed", {"status": analysis.status})
                
                await asyncio.sleep(20)
                
            except vt.APIError as e:
                await self._handle_vt_error(e)
            except aiohttp.ClientError as e:
                raise NetworkError(f"Network error retrieving results: {str(e)}")


def get_vendors_by_result(scan_results):
    """
    Extract a dictionary that groups vendor names by result type.
    
    Args:
        scan_results: Results from a VirusTotal scan
        
    Returns:
        Dict: Dictionary with result types as keys and lists of vendor names as values
    """
    vendors_by_result = {}
    
    results = scan_results.get('attributes', {}).get('results', {})
    
    for vendor_name, vendor_data in results.items():
        result = vendor_data.get('result')
        
        if result not in vendors_by_result:
            vendors_by_result[result] = []
            
        vendors_by_result[result].append(vendor_name)
    
    return vendors_by_result
