import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

import asyncio
import math
from typing import Dict, List, Optional, Union, Any, Set, DefaultDict, Tuple, TypedDict
from urllib.parse import urlparse
from datetime import datetime, timedelta
from django.utils import timezone
from django.template.loader import render_to_string
from django.db import transaction
from asgiref.sync import sync_to_async
from collections import defaultdict
import types

# Import models and related modules
from apps.config.models import Configuration
from apps.entities.models import Platform, EntityFocalPoint
from apps.alertes.models import Alert
from apps.defacement.models import Defacement
from .analyseScan import capture_and_analyze, ConfigurationError, SSLError, CaptureError, ProxyError
from .defacementCheck import compare_captures, visualize_tree
from .domainScan import DomainChecker, WhoisVerificationError, DNSResolutionError, DNSServerError, AllDNSServersFailedError, DomainExpirationError
from .siteScan import WebsiteChecker, WebsiteHttpError, WebsiteTimeoutError, WebsiteUnavailableError, WebsiteCheckerError, WebsiteSSLError, AllProxiesFailedError
from .sslScan import SSLChecker, CertificateError, CertificateExpirationWarning, ConnectionError, SSLHandshakeError
from .models import SSLScanCriteria, DomainScanCriteria, WebsiteScanCriteria, Scan
from apps.mail_setting.tasks import send_email_task

import logging
logger = logging.getLogger(__name__)


class AlertInfo(TypedDict):
    """Type definition for alert information structure."""
    name: str
    platforms: List[str]
    points_focaux: List[Dict[str, str]]


class Monitoring:
    """
    A comprehensive monitoring system for web platforms.
    
    This class handles various checks for web platforms including:
    - Domain availability and expiration
    - SSL certificate validation and expiration
    - Website availability
    - Website defacement detection
    
    It also manages alerting via email when issues are detected.
    """
    
    def __init__(self):
        """Initialize the Monitoring class with default configuration."""
        
        # Default configuration values
        self.config = None
        self.scan_config: Dict[str, Any] = {}
        self.use_host_on_proxy_fail: bool = False
        self.plateforms: List[Platform] = []
        self.max_workers: int = 1
        self.check_ssl_error: bool = True
        self.check_ssl_expiry: bool = True
        self.check_whois: bool = True
        self.check_dns_servers: bool = True
        self.check_domain_expiry_error: bool = True
        self.max_response_time_ms: int = 5
        self.receivedEmail: str = 'email@example.com'
        self.can_receiveEmail: bool = True
        self.scan_config = {
            "proxy_list": [], 
            "user_agent": 'Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0', 
            'timeout': 5
        }
        self.new_alert: bool = False
        self.use_proxy: bool = False
        
        # Define alert types and their properties
        self.collected_alerts: DefaultDict[str, DefaultDict[str, AlertInfo]] = defaultdict(
            lambda: defaultdict(lambda: {'name': '', 'platforms': [], 'points_focaux': []})
        )
        
        # Scan activation flags - will be populated from database
        self.scanSSL: bool = False
        self.scanDomain: bool = False
        self.scanDefacement: bool = False
        self.scanWebsite: bool = False
        
        # Configuration objects from database
        self.SSL_Scan_Criteria = None
        self.Domain_Scan_Criteria = None
        self.Website_Scan_Criteria = None
        self.scanPerm = None
        
        # Will be populated during initialization
        self.alert_type_names: Dict[str, str] = {}
        self.alert_colors: Dict[str, str] = {}

    async def initialize(self) -> None:
        """
        Initialize the monitoring configuration from the database.
        
        This method loads all necessary configuration from the database,
        including scan criteria, proxy settings, and platform information.
        """
        
        # Load scan permission settings
        self.scanPerm = await sync_to_async(Scan.objects.all)()
        
        # Get scan type activation status
        self.scanSSL = await sync_to_async(lambda: self.scanPerm.filter(code='ssl').first().is_active)()
        self.scanDomain = await sync_to_async(lambda: self.scanPerm.filter(code='domain').first().is_active)()
        self.scanDefacement = await sync_to_async(lambda: self.scanPerm.filter(code='defacement').first().is_active)()
        self.scanWebsite = await sync_to_async(lambda: self.scanPerm.filter(code='website').first().is_active)()
        
        # Load global configuration
        self.config = await sync_to_async(Configuration.objects.first)()

        # Load SSL scan criteria
        self.SSL_Scan_Criteria = await sync_to_async(SSLScanCriteria.objects.first)()
        if self.SSL_Scan_Criteria:
            self.check_ssl_error = self.SSL_Scan_Criteria.check_ssl_error
            self.check_ssl_expiry = self.SSL_Scan_Criteria.check_ssl_expiry

        # Load domain scan criteria
        self.Domain_Scan_Criteria = await sync_to_async(DomainScanCriteria.objects.first)()
        if self.Domain_Scan_Criteria:
            self.check_whois = self.Domain_Scan_Criteria.check_whois
            self.check_dns_servers = self.Domain_Scan_Criteria.check_dns_servers
            self.check_domain_expiry_error = self.Domain_Scan_Criteria.check_domain_expiry_error
        
        # Load website scan criteria
        self.Website_Scan_Criteria = await sync_to_async(WebsiteScanCriteria.objects.first)()
        if self.Website_Scan_Criteria:
            self.scan_config['timeout'] = math.ceil(self.Website_Scan_Criteria.max_response_time_ms / 1000)
        
        # Configure proxy settings
        if self.config.use_proxy and self.config.proxy:
            self.scan_config['proxy_list'] = self.config.proxy
        if self.config.user_agent:
            self.scan_config['user_agent'] = self.config.user_agent
        
        # Set global settings
        self.use_host_on_proxy_fail = self.config.use_host_on_proxy_fail
        self.use_proxy = self.config.use_proxy
        self.receivedEmail = self.config.email
        self.can_receiveEmail = self.config.receive_alert
        
        # Load active platforms
        platforms_queryset = Platform.objects.select_related('domain', 'entity').filter(is_active=True)
        self.plateforms = await sync_to_async(list)(platforms_queryset)
        
        self.max_workers = self.config.max_worker
        
        # Initialize alert collections
        self.collected_alerts = {
            'ssl': defaultdict(lambda: {'name': '', 'platforms': [], 'points_focaux': []}),
            'ssl_expiredSoon': defaultdict(lambda: {'name': '', 'platforms': [], 'points_focaux': []}),
            'domain_unvailable': defaultdict(lambda: {'name': '', 'platforms': [], 'points_focaux': []}),
            'domain_expiredSoon': defaultdict(lambda: {'name': '', 'platforms': [], 'points_focaux': []}),
            'availability': defaultdict(lambda: {'name': '', 'platforms': [], 'points_focaux': []}),
            'defacement': defaultdict(lambda: {'name': '', 'platforms': [], 'points_focaux': []})
        }

        self.alert_type_names = {
            'ssl': 'SSL Certificates issues',
            'ssl_expiredSoon': 'SSL Certificates expiring soon',
            'domain_unvailable': 'Domains unavailable',
            'domain_expiredSoon': 'Domains expiring soon',
            'availability': 'Website availability issues',  
            'defacement': 'Defacement issues'
        }
        
        self.alert_colors = {
            'ssl': '#e53935',  # Red
            'ssl_expiredSoon': '#fb8c00',  # Orange
            'domain_unvailable': '#e53935',  # Red
            'domain_expiredSoon': '#fb8c00',  # Orange
            'availability': '#e53935',  # Red
            'defacement': '#d32f2f'  # Dark red
        }

    async def collect_alert(self, platform: Platform, alert_type: str) -> None:
        """
        Collect alert information for a platform and alert type.
        
        Args:
            platform: The platform that has an issue
            alert_type: The type of alert being collected
            
        Sets the new_alert flag to True and adds the alert to the collection.
        """
        self.new_alert = True
        
        try:
            entity_id = str(platform.entity.id)
            
            # If this is the first alert for this entity, get the entity details
            if not self.collected_alerts[alert_type][entity_id]['name']:
                self.collected_alerts[alert_type][entity_id]['name'] = platform.entity.name
                
                # Get focal points for the entity - using the correct way to chain select_related
                # First get the queryset with select_related
                queryset = EntityFocalPoint.objects.filter(
                    entity_id=platform.entity.id
                ).select_related('focal_point', 'focal_point__function')
                
                # Then make it async
                entity_focal_points = await sync_to_async(queryset.exists)()
                
                if entity_focal_points:
                    # Convert queryset to list for async processing
                    focal_points_list = await sync_to_async(list)(queryset)
                    
                    # Extract focal point details
                    self.collected_alerts[alert_type][entity_id]['points_focaux'] = [
                        {
                            'name': efp.focal_point.full_name,
                            'email': efp.focal_point.email,
                            'phone': efp.focal_point.phone_number[0] if efp.focal_point.phone_number else ''
                        } for efp in focal_points_list if efp.focal_point and efp.focal_point.is_active
                    ]
            
            # Add platform URL to the list if not already present
            if platform.url not in self.collected_alerts[alert_type][entity_id]['platforms']:
                self.collected_alerts[alert_type][entity_id]['platforms'].append(platform.url)
                
        
        except Exception as e:
            logger.error(f"Error collecting alert for {platform.url}: {str(e)}", exc_info=True)
            # We don't re-raise the exception to avoid breaking the monitoring flow

    async def process_collected_alerts(self) -> int:
        """
        Process all collected alerts and send a consolidated report.
        
        Returns:
            int: The number of affected platforms
        """
        try:
            # Calculate statistics for the report
            alert_stats = {alert_type: sum(len(entity_data['platforms']) for entity_data in entities.values())
                          for alert_type, entities in self.collected_alerts.items()}
            
            # Get unique affected platforms
            total_affected_platforms: Set[str] = set()
            for alert_type, entities in self.collected_alerts.items():
                for entity_data in entities.values():
                    total_affected_platforms.update(entity_data['platforms'])
            
            # convert defaultdict to regular dict for serialization
            regular_alerts = {}
            for alert_type, entities in self.collected_alerts.items():
                regular_alerts[alert_type] = dict(entities)

            # Prepare context for the email template
            context = {
                'alerts': regular_alerts,
                'alert_type_names': self.alert_type_names,
                'alert_colors': self.alert_colors,
                'alert_stats': alert_stats,
                'total_platforms': len(self.plateforms),
                'total_affected_platforms': len(total_affected_platforms),
                'report_date': timezone.now()
            }
            
            html_content = await sync_to_async(render_to_string)('resumeAlert.html', context)
            
            # Determine email subject based on the severity
            percentage = (len(total_affected_platforms) / len(self.plateforms)) * 100 if self.plateforms else 0
            if percentage >= 50:
                subject = f"[URGENT] Oju Monitoring - {len(total_affected_platforms)} sites with issues ({percentage:.1f}%)"
            elif percentage >= 25:
                subject = f"[IMPORTANT] Oju Monitoring - {len(total_affected_platforms)} sites with issues ({percentage:.1f}%)"
            else:
                subject = f"Oju Monitoring - {len(total_affected_platforms)} sites with issues ({percentage:.1f}%)"
            
            # Send email if there are affected platforms and email is enabled
            if len(total_affected_platforms) > 0 and self.can_receiveEmail:
                send_email_task.delay(
                    subject=subject,
                    body=html_content,
                    to_recipients=[self.receivedEmail],
                    is_html=True
                )
            else:
                pass
            return len(total_affected_platforms)
            
        except Exception as e:
            logger.error(f"Error processing collected alerts: {str(e)}", exc_info=True)
            return 0

    async def resolve_existing_alerts(self, platform: Platform, alert_type: str) -> Tuple[Optional[Alert], bool]:
        """
        Resolve existing alerts for a platform and alert type.
        
        Args:
            platform: The platform to resolve alerts for
            alert_type: The type of alert to resolve
            
        Returns:
            Tuple[Optional[Alert], bool]: The resolved alert and whether it was resolved
        """
        try:
            # Get the most recent active alert
            last_alert = await sync_to_async(
                Alert.objects.select_related('platform', 'entity').filter(
                    platform=platform,
                    alert_type=alert_type,
                    status__in=['in_progress', 'new'] 
                ).order_by('-created_at').first
            )()

            if last_alert:
                
                current_time = timezone.now()
                
                # Update alert status
                last_alert.status = 'resolved'
                last_alert.updated_at = current_time
                await sync_to_async(last_alert.save)()
                
                # Prepare email notification
                templates = await sync_to_async(render_to_string)(
                    'IssuesResolved.html',
                    {
                        "alert_type_display": last_alert.get_alert_type_display(),
                        "site_url": platform.url,
                        "created_at": last_alert.created_at.strftime('%d/%m/%Y at %H:%M'),
                        "resolved_at": current_time.strftime('%d/%m/%Y at %H:%M'),
                        "details": last_alert.details
                    }
                )
                
                # Send email notification if enabled
                if not self.can_receiveEmail:
                    return last_alert, True
                
                send_email_task.delay(
                    subject=f"Oju Alert: {last_alert.get_alert_type_display()} - {last_alert.platform.url} Resolved",
                    body=templates,
                    to_recipients=[self.receivedEmail],
                    is_html=True
                )
                
                return last_alert, True
            else:
                return None, False            
            
        except Exception as e:
            logger.error(f"Error resolving alerts for {platform.url}: {str(e)}", exc_info=True)
            return None, False

    async def get_or_create_defacement(self, platform: Platform) -> Tuple[Defacement, bool]:
        """
        Get or create a defacement record for a platform.
        
        Args:
            platform: The platform to get or create a defacement record for
            
        Returns:
            Tuple[Defacement, bool]: The defacement record and whether it was created
        """
        try:
            defacement, created = await sync_to_async(Defacement.objects.get_or_create)(
                platform=platform,
                defaults={
                    'entity': platform.entity,
                    'date': timezone.now(),
                    'is_defaced': False,
                    'normal_state': {},
                    'last_state': {},
                    'normal_state_tree': '',
                    'last_state_tree': ''
                }
            )
                            
            return defacement, created
        except Exception as e:
            logger.error(f"Error getting/creating defacement for {platform.url}: {str(e)}", exc_info=True)
            raise

    async def update_platform(self, platform: Platform, **kwargs) -> Platform:
        """
        Update a platform with the given attributes.
        
        Args:
            platform: The platform to update
            **kwargs: The attributes to update
            
        Returns:
            Platform: The updated platform
        """
        try:
            # Update each attribute
            for key, value in kwargs.items():
                setattr(platform, key, value)
            
            # Save the platform
            await sync_to_async(platform.save)()
            
            return platform
        except Exception as e:
            logger.error(f"Error updating platform {platform.url}: {str(e)}", exc_info=True)
            raise

    async def update_defacement(self, defacement: Defacement, **kwargs) -> Defacement:
        """
        Update a defacement record with the given attributes.
        
        Args:
            defacement: The defacement record to update
            **kwargs: The attributes to update
            
        Returns:
            Defacement: The updated defacement record
        """
        platform_url = await sync_to_async(lambda: defacement.platform.url)()
        try:
            # Update each attribute
            for key, value in kwargs.items():
                setattr(defacement, key, value)
            
            # Set date if not provided
            if 'date' not in kwargs:
                defacement.date = timezone.now()
                
            # Save the defacement record
            await sync_to_async(defacement.save)()
            
            return defacement
        except Exception as e:
            logger.error(f"Error updating defacement for {platform_url}: {str(e)}", exc_info=True)
            raise

    async def check_existing_alert(self, platform: Platform, alert_type: str) -> bool:
        """
        Check if an active alert already exists for a platform and alert type.
        
        Args:
            platform: The platform to check alerts for
            alert_type: The type of alert to check
            
        Returns:
            bool: True if an active alert exists, False otherwise
        """
        
        # Check if any active alerts exist
        exists = await sync_to_async(
            Alert.objects.filter(
                platform=platform,
                alert_type=alert_type,
                status__in=['in_progress', 'new']
            ).exists
        )()
        
        return exists
    
    async def check_day_existing_alert(self, platform: Platform, alert_type: str) -> bool:
        """
        Check if an active alert created today exists for a platform and alert type.
        
        Args:
            platform: The platform to check alerts for
            alert_type: The type of alert to check
            
        Returns:
            bool: True if an active alert created today exists, False otherwise
        """
        
        # Get the start of today
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Check if any active alerts created today exist
        exists = await sync_to_async(
            Alert.objects.filter(
                platform=platform,
                alert_type=alert_type,
                created_at__gte=today,
                status__in=['in_progress', 'new']
            ).exists
        )()
        
        return exists
    
    async def create_alert(self, platform: Platform, details: str, templates: str, alert_type: str) -> None:
        """
        Create a new alert for an identified issue.
        
        Args:
            platform: The platform with the issue
            details: Details about the issue
            templates: Email template content for notification
            alert_type: The type of alert to create
        """
        # First try to collect the alert for reporting
        try:
            await self.collect_alert(platform, alert_type)
        except Exception as e:
            logger.error(f"Error collecting alert for {platform.url}: {str(e)}", exc_info=True)
            # Continue even if collection fails
        
        try:
            # Create the alert in the database
            await sync_to_async(Alert.objects.create)(
                entity=platform.entity,
                platform=platform,
                alert_type=alert_type,
                details=details,
                templates=templates
            )
        except Exception as e:
            logger.error(f"Error creating alert for {platform.url}: {str(e)}", exc_info=True)
            raise

    async def update_domain(self, domain, **kwargs) -> None:
        """
        Update domain information.
        
        Args:
            domain: The domain to update
            **kwargs: The attributes to update
        """
        try:
            # Update each attribute
            for key, value in kwargs.items():
                setattr(domain, key, value)
            
            # Save the domain
            await sync_to_async(domain.save)()
        except Exception as e:
            logger.error(f"Error updating domain {domain.name}: {str(e)}", exc_info=True)
            raise

    async def handle_domain_check(self, platform: Platform, domain_) -> bool:
        """
        Manage domain verification checks.
        
        Args:
            platform: The platform associated with the domain
            domain_: The domain to check
            
        Returns:
            bool: True if the domain check was successful, False otherwise
        """
        try:
            # Skip check if domain was recently checked and had no issues
            now = timezone.now()
            last_scan = domain_.last_scan_date
            
            if last_scan and (now - last_scan < timedelta(hours=1)) and not domain_.domain_issue:
                return True
                
            # Create domain checker with appropriate settings
            domain_checker = DomainChecker(
                domain_.name, 
                check_whois=self.check_whois, 
                check_dns_server=self.check_dns_servers, 
                check_domain_expiry_error=self.check_domain_expiry_error,
                timeout=self.max_response_time_ms
            )
            
            # Run the domain check
            result = await sync_to_async(domain_checker.check)()
            
            # If successful, resolve any existing alerts
            await self.resolve_existing_alerts(platform, 'domain_unvailable')
            # await self.resolve_existing_alerts(platform, 'domain_expiredSoon')
            
            # Update domain information
            await self.update_domain(domain_,
                ip_address=result['resolved_ip'],
                last_scan_date=timezone.now(),
                domain_issue=False
            )
            return True
            
        except DomainExpirationError as e:
            # Handle domain expiration warnings
            
            # Create alert if one doesn't exist today
            if not await self.check_day_existing_alert(platform, 'domain_expiredSoon'):
                templates = await sync_to_async(render_to_string)(
                    'DomainExpired.html',
                    {"domain": domain_.name, "remaining_days": e.to_dict()["day_remaining"]}
                )
                await self.create_alert(platform, str(e), templates, 'domain_expiredSoon')
                    
            # Update domain information
            await self.update_domain(domain_,
                last_scan_date=timezone.now(),
                domain_issue=False
            )
            return True

        except (WhoisVerificationError, DNSResolutionError, DNSServerError, AllDNSServersFailedError) as e:
            # Handle domain unavailability errors
            
            # Create alert if one doesn't exist
            if not await self.check_existing_alert(platform, 'domain_unvailable'):
                templates = await sync_to_async(render_to_string)(
                    'DomainIssues.html',
                    {"domain": domain_.name}
                )
                await self.create_alert(platform, str(e), templates, 'domain_unvailable')
                
            # Update domain information
            await self.update_domain(domain_,
                last_scan_date=timezone.now(),
                domain_issue=True
            )
            return False
            
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error in domain check for {domain_.name}: {str(e)}", exc_info=True)
            
            # Update domain information
            await self.update_domain(domain_,
                last_scan_date=timezone.now(),
                domain_issue=True
            )
            return False


    async def handle_site_check(self, platform: Platform, site_checker: WebsiteChecker) -> bool:
        """
        Manage website availability verification.
        
        Args:
            platform: The platform to check
            site_checker: The website checker instance
            
        Returns:
            bool: True if the site check was successful, False otherwise
        """
        try:
            # Run the site check
            await sync_to_async(site_checker.check)(platform.url)

            # If successful, resolve any existing alerts
            await self.resolve_existing_alerts(platform, 'availability')

            return True
        
        except AllProxiesFailedError as error:
            # Special handling for proxy failures
            if error.to_dict().get('is_proxy_issue', False):
                logger.critical(f"All proxies failed for {platform.url}: {str(error)}")
            
            
            # Try direct connection if configured to do so
            if self.use_host_on_proxy_fail and self.use_proxy:
                try:
                    # Create a direct checker without proxies
                    direct_checker = WebsiteChecker(
                        user_agent=self.scan_config.get('user_agent'),
                        timeout=self.scan_config.get('timeout', 10)
                    )
                    
                    # Check the site directly
                    await sync_to_async(direct_checker.check)(platform.url)
                    
                    # If successful, resolve any existing alerts
                    await self.resolve_existing_alerts(platform, 'availability')
                    
                    return True
                    
                except WebsiteSSLError as e:
                    # SSL errors are handled in the SSL check
                    return True
                    
                except (WebsiteHttpError, WebsiteTimeoutError, WebsiteUnavailableError, WebsiteCheckerError) as error:
                    # Handle website availability errors in direct connection
                    
                    # Create alert if one doesn't exist
                    if not await self.check_existing_alert(platform, 'availability'):
                        templates = await sync_to_async(render_to_string)(
                            'SiteIssues.html',
                            {"site_url": platform.url}
                        )
                        await self.create_alert(platform, str(error), templates, 'availability')
                    
                    return False
                    
                except Exception as e:
                    # Handle unexpected errors
                    logger.error(f"Unexpected error in direct site check for {platform.url}: {str(e)}", exc_info=True)
                    return False
            
            # If not using direct connection fallback
            if not self.use_host_on_proxy_fail:
                if not error.to_dict().get('is_proxy_issue', False):
                    # This is a real site issue, not just proxy issues
                    
                    # Create alert if one doesn't exist
                    if not await self.check_existing_alert(platform, 'availability'):
                        templates = await sync_to_async(render_to_string)(
                            'SiteIssues.html',
                            {"site_url": platform.url}
                        )
                        await self.create_alert(platform, str(error), templates, 'availability')
                else:
                    # All proxies failed but it might be a proxy issue, not a site issue
                    logger.critical(f"All proxies failed for {platform.url}: {str(error)}, to avoid false positive, alert will not be created")
            
            return False

        except WebsiteSSLError as e:
            # SSL errors are handled in the SSL check, not here
            return True

        except (WebsiteHttpError, WebsiteTimeoutError, WebsiteUnavailableError) as e:
            # Handle website availability errors
            
            # Create alert if one doesn't exist
            if not await self.check_existing_alert(platform, 'availability'):
                templates = await sync_to_async(render_to_string)(
                    'SiteIssues.html',
                    {"site_url": platform.url}
                )
                await self.create_alert(platform, str(e), templates, 'availability')
            
            return False
            
        except WebsiteCheckerError as e:
            return False
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error in site check for {platform.url}: {str(e)}", exc_info=True)
            return False
            

    async def _perform_ssl_check(self, domain_name: str, port: int, platform: Platform, proxy_urls: Optional[List[str]] = None) -> bool:
        """
        Helper method to perform SSL certificate check.
        
        Args:
            domain_name: The domain name to check
            port: The port to check
            platform: The platform associated with the domain
            proxy_urls: Optional list of proxy URLs to use
            
        Returns:
            bool: True if the SSL check was successful, False otherwise
        """
        try:
            # Create SSL checker with appropriate configuration
            ssl_checker = SSLChecker(
                domain_name, 
                port, 
                proxy_urls, 
                self.scan_config.get('timeout', 10),
                self.check_ssl_error, 
                self.check_ssl_expiry
            )
            
            # Verify the certificate
            await sync_to_async(ssl_checker.verify_certificate)()
            
            # If successful, resolve any existing alerts
            await self.resolve_existing_alerts(platform, 'ssl')
            # await self.resolve_existing_alerts(platform, 'ssl_expiredSoon')
            
            return True
            
        except CertificateExpirationWarning as e:
            # Handle certificate expiration warnings
            
            # Create alert if one doesn't exist today
            if not await self.check_day_existing_alert(platform, 'ssl_expiredSoon'):
                templates = await sync_to_async(render_to_string)(
                    'SSLExpired.html',
                    {"site_url": platform.url, "remaining_days": e.to_dict().get("days_remaining")}
                )
                await self.create_alert(platform, str(e), templates, 'ssl_expiredSoon')
            
            # This is a warning, not an error
            return True
            
        except CertificateError as e:
            # Handle certificate errors
            
            # Create alert if one doesn't exist
            if not await self.check_existing_alert(platform, 'ssl'):
                templates = await sync_to_async(render_to_string)(
                    'SSLIssues.html',
                    {"site_url": platform.url, "details": str(e)}
                )
                await self.create_alert(platform, str(e), templates, 'ssl')
            
            return False
        except (AllProxiesFailedError, ProxyError) as e:
            raise
        except SSLHandshakeError as e:
            return False
        except ConnectionError as e:
            # Handle connection errors
            return False
        
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error in SSL check for {domain_name}: {str(e)}", exc_info=True)
            return False

    async def handle_ssl_check(self, platform: Platform, domain_) -> bool:
        """
        Manage SSL certificate verification.
        
        Args:
            platform: The platform to check
            domain_: The domain associated with the platform
            
        Returns:
            bool: True if the SSL check was successful, False otherwise
        """
        
        # Parse URL to get port and check if HTTPS
        temp_parse = urlparse(platform.url)
        port = int(temp_parse.netloc.split(':')[1]) if ':' in temp_parse.netloc else 443
        
        # Skip SSL check for non-HTTPS sites
        if temp_parse.scheme != "https":
            return True

        try:
            # Perform the SSL check with proxies if configured
            ssl_result = await self._perform_ssl_check(
                domain_.name, 
                port, 
                platform,
                self.scan_config.get('proxy_list')
            )
            
            if ssl_result:
                await self.update_domain(domain_,
                    last_ssl_scan_date=timezone.now(),
                    ssl_issue=False
                )
                return True
            else:
                # The specific error has already been handled in _perform_ssl_check
                await self.update_domain(domain_,
                    last_ssl_scan_date=timezone.now(),
                    ssl_issue=True
                )
                return False
                
        except (AllProxiesFailedError, ProxyError) as error:
            # Special handling for proxy failures
            
            # if error.to_dict().get('is_proxy_issue', False):
            #     logger.critical(f"All proxies failed for {domain_.name}: {str(error)}")
            
            # Try direct connection if configured to do so
            if self.use_host_on_proxy_fail and self.use_proxy:
                
                # Perform direct SSL check
                direct_result = await self._perform_ssl_check(
                    domain_.name,
                    port,
                    platform,
                    None  # No proxies
                )
                
                if direct_result:
                    await self.update_domain(domain_,
                        last_ssl_scan_date=timezone.now(),
                        ssl_issue=False
                    )
                    return True
                else:
                    # The specific error has already been handled in _perform_ssl_check
                    await self.update_domain(domain_,
                        last_ssl_scan_date=timezone.now(),
                        ssl_issue=True
                    )
                    return False
            
            # If not using direct connection fallback
            if not self.use_host_on_proxy_fail:
                if not error.to_dict().get('is_proxy_issue', False):
                    # This is a real SSL issue, not just proxy issues
                    
                    # Create alert if one doesn't exist
                    if not await self.check_existing_alert(platform, 'ssl'):
                        templates = await sync_to_async(render_to_string)(
                            'SSLIssues.html',
                            {"site_url": platform.url, "details": str(error)}
                        )
                        await self.create_alert(platform, str(error), templates, 'ssl')
                else:
                    pass
                    # All proxies failed but it might be a proxy issue, not an SSL issue
                    # logger.critical(f"All proxies failed for {domain_.name}:{port}: {str(error)}, to avoid false positive, alert will not be created")
            
            # Update domain information
            await self.update_domain(domain_,
                last_ssl_scan_date=timezone.now(),
                ssl_issue=True
            )
            return False
            
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error in SSL check for {domain_.name}: {str(e)}", exc_info=True)
            
            # Update domain information
            await self.update_domain(domain_,
                last_ssl_scan_date=timezone.now(),
                ssl_issue=True
            )
            return False


    async def handle_defacement_check(self, platform: Platform) -> bool:
        """
        Manage defacement verification for a website.
        
        Args:
            platform: The platform to check for defacement
            
        Returns:
            bool: True if the defacement check was successful, False otherwise
        """
        
        # First, capture and analyze the website's current state
        try:
            analyse = await capture_and_analyze({
                "url": platform.url,
                "user_agent": self.scan_config.get("user_agent"),
                "proxy_list": self.scan_config.get("proxy_list"),
                "max_time": self.max_response_time_ms
            })
        
        except ProxyError as e:
            # If proxy error, try direct connection if configured
            if self.use_host_on_proxy_fail and self.use_proxy:
                try:
                    analyse = await capture_and_analyze({
                        "url": platform.url,
                        "user_agent": self.scan_config.get("user_agent"),
                        "max_time": self.max_response_time_ms
                    })
                except (ConfigurationError, SSLError, TimeoutError, CaptureError) as e:
                    return False
                except Exception as e:
                    return False
            else:
                return False

        except (ConfigurationError, SSLError, TimeoutError, CaptureError) as e:
            # Handle capture errors
            logger.error(f"Capture error for {platform.url}: {str(e)}")
            return False
                   
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error in capturing HAR for {platform.url}: {str(e)}", exc_info=True)
            return False

        # Now process the captured data
        try:
            defacement, created = await self.get_or_create_defacement(platform)
            
            if created:
                await self.update_defacement(defacement,
                    entity=platform.entity,
                    date=timezone.now(),
                    is_defaced=False,
                    normal_state=analyse,
                    normal_state_tree=visualize_tree(analyse['tree'])
                )
            else:
                # Compare current state with baseline
                
                if defacement.normal_state and analyse.get('tree'):
                    # Compare the current state with the baseline
                    changes = await compare_captures(
                        defacement.normal_state,
                        analyse
                    )
                    
                    if changes:
                        # Defacement detected
                        
                        # Create alert if one doesn't exist
                        if not await self.check_existing_alert(platform, 'defacement'):
                            templates = await sync_to_async(render_to_string)(
                                'Defacement.html',
                                {"site_url": platform.url}
                            )
                            await self.create_alert(platform, changes, templates, 'defacement')
                            
                            # Update defacement record
                            await self.update_defacement(defacement,
                                is_defaced=True,
                                last_state=analyse,
                                date=timezone.now(),
                                details=changes,
                                last_state_tree=visualize_tree(analyse.get("tree"))
                            )
                    else:
                        # No defacement detected
                        await self.resolve_existing_alerts(platform, 'defacement')
                        
                        # Update defacement record
                        await self.update_defacement(defacement,
                            is_defaced=False,
                            date=timezone.now(),
                            last_state=analyse,
                            last_state_tree=visualize_tree(analyse.get("tree")),
                            details=''
                        )

            import base64, os
            from django.conf import settings
            screenshots_dir = os.path.join(settings.MEDIA_ROOT, 'screenshots')
            os.makedirs(screenshots_dir, exist_ok=True)
            screenshot_filename = f"{platform.id}.png"
            screenshot_path = os.path.join(screenshots_dir, screenshot_filename)
            if analyse.get('screenshot'):
                try:
                    
                    base64_data = analyse.get('screenshot').split(',')[1] if ',' in analyse.get('screenshot') else analyse.get('screenshot')
                    with open(screenshot_path, "wb") as f:
                        f.write(base64.b64decode(base64_data))
                    await self.update_platform(platform, screenshot=f"screenshots/{screenshot_filename}")
                except Exception as e:
                    if os.path.exists(screenshot_path):
                        try:
                            os.remove(screenshot_path)
                        except Exception as e_remove:
                            logger.error(f"Failed to remove screenshot file: {str(e_remove)}")
                    
                    await self.update_platform(platform, screenshot=None)
            else:
                if os.path.exists(screenshot_path):
                    try:
                        os.remove(screenshot_path)
                    except Exception as e_remove:
                        logger.error(f"Failed to remove screenshot file: {str(e_remove)}")
                
                await self.update_platform(platform, screenshot=None)
                
        except Exception as e:
            # Handle unexpected errors in processing
            logger.error(f"Unexpected error while registering defacement values: {str(e)}", exc_info=True)
            return False
            
        return True

    async def process_platform(self, platform: Platform) -> None:
        """
        Process all checks for an individual platform.
        
        Args:
            platform: The platform to process
        """
        import base64, os
        from django.conf import settings
        screenshots_dir = os.path.join(settings.MEDIA_ROOT, 'screenshots')
        os.makedirs(screenshots_dir, exist_ok=True)
        screenshot_filename = f"{platform.id}.png"
        screenshot_path = os.path.join(screenshots_dir, screenshot_filename)
        try:
            # Get domain associated with the platform
            domain_ = platform.domain

            # Domain check
            if self.scanDomain:
                domain_ok = await self.handle_domain_check(platform, domain_)
                if not domain_ok:
                    if os.path.exists(screenshot_path):
                        try:
                            os.remove(screenshot_path)
                        except Exception as e_remove:
                            logger.error(f"Failed to remove screenshot file: {str(e_remove)}")
                
                    await self.update_platform(platform, screenshot=None)
                    return

            # Website availability check
            if self.scanWebsite:
                site_checker = WebsiteChecker(
                    proxy_list=self.scan_config.get("proxy_list", []),
                    user_agent=self.scan_config.get('user_agent'),
                    timeout=self.scan_config.get('timeout')
                )
                site_ok = await self.handle_site_check(platform, site_checker)
                if not site_ok:
                    if os.path.exists(screenshot_path):
                        try:
                            os.remove(screenshot_path)
                        except Exception as e_remove:
                            logger.error(f"Failed to remove screenshot file: {str(e_remove)}")
                    await self.update_platform(platform, screenshot=None)
                    return

            # SSL certificate check
            if self.scanSSL:
                ssl_ok = await self.handle_ssl_check(platform, domain_)
                if not ssl_ok:
                    pass
                    # Not returning here as we still want to check for defacement

            # Defacement check
            if self.scanDefacement:
                await self.handle_defacement_check(platform)
            
        except Exception as e:
            logger.error(f"Unexpected error processing platform {platform.url}: {str(e)}", exc_info=True)


    async def process_batch(self, batch: List[Platform]) -> None:
        """
        Process a batch of platforms concurrently.
        
        Args:
            batch: The list of platforms to process
        """
        try:
            tasks = [self.process_platform(platform) for platform in batch]
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error processing batch: {str(e)}", exc_info=True)


    async def run(self) -> None:
        """
        Main method to run all monitoring checks on all platforms.
        
        This method initializes the configuration, divides platforms into batches,
        processes each batch concurrently, and generates a consolidated report.
        """
        try:
            # Initialize configuration
            await self.initialize()
            
            logger.info(f"Starting monitoring with {self.max_workers} workers")
            total_platforms = len(self.plateforms)
            
            if total_platforms == 0:
                logger.warning("No active platforms found to monitor")
                return
            
            # Create a semaphore to limit concurrent workers to max_workers
            semaphore = asyncio.Semaphore(self.max_workers)

            async def process_platform_with_semaphore(platform):
                async with semaphore:
                    await self.process_platform(platform)

            # Process all platforms concurrently
            await asyncio.gather(*[process_platform_with_semaphore(platform) for platform in self.plateforms])
            
            

            # Generate consolidated report
            affected_count = await self.process_collected_alerts()
        
            if affected_count > 0:
                logger.info(f"Consolidated report generated for {affected_count} affected platforms")
            else:
                logger.info("No issues detected, no report generated")
            
        except Exception as e:
            logger.error(f"Error during monitoring run: {str(e)}", exc_info=True)
            raise
        finally:
            logger.info("Monitoring run completed")