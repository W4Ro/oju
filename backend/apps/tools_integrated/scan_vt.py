import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from django.db import transaction
from django.utils import timezone
from django.template.loader import render_to_string
from asgiref.sync import sync_to_async

from apps.entities.models import Platform, EntityFocalPoint
from apps.alertes.models import Alert
from apps.config.models import Configuration
from apps.tools_integrated.models import VirusTotal
from apps.AV_vendor.models import AVVendor
from apps.tools_integrated.virustotal import VirusTotalScanner, get_vendors_by_result
from apps.tools_integrated.virustotal import (
    APIKeyError, NetworkError, RateLimitError, ScanError, ResourceNotFoundError,
    ValidationError, ConfigurationError, AnalysisError, TimeoutError,
    AuthenticationError, PermissionError, ServiceUnavailableError
)

logger = logging.getLogger(__name__)

class VirusTotalTask:
    """Task for scanning platforms with VirusTotal."""
    
    def __init__(self):
        """Initialize the VirusTotal task."""
        logger.info("Initializing VirusTotal scan task")
        
        self.vt_config = None
        self.api_key = None
        self.max_workers = 5 
        self.scanner = None
        self.platforms = []
        self.receive_email = 'exempla@exemple.com'
        self.can_receive_email = False
        
    async def initialize(self) -> bool:
        """
        Initialize the task by loading configuration and validating API key.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        logger.info("Starting initialization of VirusTotal task")
        
        try:
            self.vt_config = await sync_to_async(VirusTotal.objects.first)()
            
            if not self.vt_config:
                logger.error("No VirusTotal configuration found in database")
                return False
                
            if not self.vt_config.is_active:
                logger.info("VirusTotal scanning is disabled in configuration")
                return False
                
            self.api_key = self.vt_config.api_key
            
            if not self.api_key:
                logger.error("No VirusTotal API key configured")
                return False
            
            config = await sync_to_async(Configuration.objects.first)()
            if not config:
                logger.error("No configuration found in database")
                return False
            self.max_workers = config.max_worker if config else 5
            self.receive_email = config.email
            self.can_receive_email = config.receive_alert
            
            self.scanner = VirusTotalScanner(api_key=self.api_key)
            
            try:
                is_valid = await self.scanner.verify_api_key()
                if not is_valid:
                    logger.error("VirusTotal API key validation failed")
                    return False
                logger.info("VirusTotal API key validated successfully")
            except Exception as e:
                logger.error(f"Error while trying authentication of virusTotal: {str(e)}")
                return False
            
            platforms_queryset = Platform.objects.select_related('domain', 'entity').filter(is_active=True)
            self.platforms = await sync_to_async(list)(platforms_queryset)
            # first_platform = await sync_to_async(platforms_queryset.first)()
            # if first_platform:
            #     self.platforms = [first_platform]
            # else:
            #     self.platforms = []
            
            logger.info(f"Initialization completed. Found {len(self.platforms)} active platforms")
            return True
            
        except Exception as e:
            logger.error(f"Error during initialization: {str(e)}", exc_info=True)
            return False
    
    async def check_existing_alert(self, platform: Platform) -> bool:
        """
        Check if an active VirusTotal alert already exists for a platform.
        
        Args:
            platform: The platform to check alerts for
            
        Returns:
            bool: True if an active alert exists, False otherwise
        """
        logger.info(f"Checking existing alerts for platform {platform.url}")
        
        
        exists = await sync_to_async(
            Alert.objects.filter(
                platform=platform,
                alert_type='vt',
                status__in=['in_progress', 'new']
            ).exists
        )()
        
        logger.info(f"VirusTotal alert exists for {platform.url}: {exists}")
        return exists
    
    async def resolve_existing_alerts(self, platform: Platform) -> Tuple[Optional[Alert], bool]:
        """
        Resolve existing VirusTotal alerts for a platform.
        
        Args:
            platform: The platform to resolve alerts for
            
        Returns:
            Tuple[Optional[Alert], bool]: The resolved alert and whether it was resolved
        """
        logger.info(f"Resolving existing VirusTotal alerts for {platform.url}")
        try:
            last_alert = await sync_to_async(
                Alert.objects.select_related('platform', 'entity').filter(
                    platform=platform,
                    alert_type='vt',
                    status__in=['in_progress', 'new'] 
                ).order_by('-created_at').first
            )()

            if last_alert:
                logger.info(f"Resolving VirusTotal alert ID {last_alert.id} for {platform.url}")
                
                current_time = timezone.now()
                
                last_alert.status = 'resolved'
                last_alert.updated_at = current_time
                await sync_to_async(last_alert.save)()

                if not self.can_receive_email:
                    logger.infof(f"System is not configured to receive alerts, skipping email notification for {platform.url}:Flagged on virustotal") 
                    return last_alert, True
                
                focal_points = await self.get_entity_focal_points(platform)
                
                templates = await sync_to_async(render_to_string)(
                    'VirusTotalResolved.html',
                    {
                        "site_url": platform.url,
                        "created_at": last_alert.created_at.strftime('%d/%m/%Y at %H:%M'),
                        "resolved_at": current_time.strftime('%d/%m/%Y at %H:%M'),
                        "details": last_alert.details,
                        "points_focaux": focal_points
                    }
                )
                
                from apps.mail_setting.tasks import send_email_task
                send_email_task.delay(
                    subject=f"Oju Alert: VirusTotal issue resolved for {platform.url}",
                    body=templates,
                    to_recipients=[self.receive_email],
                    is_html=True
                )
                
                logger.info(f"VirusTotal alert resolved and notification scheduled for {platform.url}")
                return last_alert, True
            else:
                logger.info(f"No active VirusTotal alerts found for {platform.url}")
                return None, False            
            
        except Exception as e:
            logger.error(f"Error resolving VirusTotal alerts for {platform.url}: {str(e)}", exc_info=True)
            return None, False
    
    async def create_alert(self, platform: Platform, details: str, templates: str, vendor_results: Dict) -> None:
        """
        Create a new alert for a malicious URL detection.
        
        Args:
            platform: The platform with the issue
            details: Details about the issue
            templates: Email template content for notification
            vendor_results: Results from vendors that flagged the URL
        """
        logger.info(f"Creating new VirusTotal alert for {platform.url}")
        
        try:
            await sync_to_async(Alert.objects.create)(
                entity=platform.entity,
                platform=platform,
                alert_type='vt',
                details=details,
                templates=templates
            )
            logger.info(f"VirusTotal alert created successfully for {platform.url}")
        except Exception as e:
            logger.error(f"Error creating alert for {platform.url}: {str(e)}", exc_info=True)
            raise
    
    async def get_vendor_information(self, vendor_name: str) -> Dict:
        """
        Get information about a vendor from the database.
        
        Args:
            vendor_name: Name of the vendor
            
        Returns:
            Dict: Vendor information or default values if not found
        """
        try:
            vendor = await sync_to_async(
                AVVendor.objects.filter(name=vendor_name).first
            )()
            
            if vendor:
                return {
                    "id": str(vendor.id),
                    "name": vendor.name,
                    "contact": vendor.contact,
                    "comments": vendor.comments,
                    "in_database": True
                }
            
            
            return {
                "id": "unknown",
                "name": vendor_name,
                "contact": "Not available in database",
                "comments": "This antivirus vendor is not registered in our database. Please contact your administrator to add it.",
                "in_database": False
            }
            
        except Exception as e:
            logger.error(f"Error retrieving vendor information for {vendor_name}: {str(e)}", exc_info=True)
            
            return {
                "id": "error",
                "name": vendor_name,
                "contact": "Error retrieving information",
                "comments": f"Error occurred while retrieving vendor information: {str(e)}",
                "in_database": False
            }
    
    async def get_entity_focal_points(self, platform: Platform) -> List[Dict]:
        """
        Get focal points for an entity.
        
        Args:
            platform: Platform to get focal points for
            
        Returns:
            List[Dict]: List of focal points with contact information
        """
        try:
            queryset = EntityFocalPoint.objects.filter(
                entity_id=platform.entity.id
            ).select_related('focal_point', 'focal_point__function')
            
            entity_focal_points = await sync_to_async(queryset.exists)()
            
            if not entity_focal_points:
                return []
            
            focal_points_list = await sync_to_async(list)(queryset)
            
            return [
                {
                    'name': efp.focal_point.full_name,
                    'email': efp.focal_point.email,
                    'phone': efp.focal_point.phone_number[0] if efp.focal_point.phone_number else ''
                } for efp in focal_points_list if efp.focal_point and efp.focal_point.is_active
            ]
            
        except Exception as e:
            logger.error(f"Error getting focal points for {platform.url}: {str(e)}", exc_info=True)
            return []
    
    async def scan_platform(self, platform: Platform) -> None:
        """
        Scan a platform with VirusTotal and create alerts if malicious.
        
        Args:
            platform: The platform to scan
        """
        logger.info(f"Starting VirusTotal scan for {platform.url}")
        
        try:
            scan_result = await self.scanner.scan_url(platform.url)
            
            vendors_by_result = get_vendors_by_result(scan_result)
            
            malicious_results = {}
            for result_type, vendors in vendors_by_result.items():
                if result_type and result_type.lower() not in ['', 'clean', 'unrated', 'none']:
                    malicious_results[result_type] = vendors
            
            if not malicious_results:
                logger.info(f"No malicious content detected for {platform.url}")
                
                resolved_alert, was_resolved = await self.resolve_existing_alerts(platform)
                if was_resolved:
                    logger.info(f"Resolved existing VirusTotal alert for {platform.url}")
                return
            
            if await self.check_existing_alert(platform):
                logger.info(f"Skipping scan for {platform.url} as alert already exists")
                return

            logger.warning(f"Malicious content detected for {platform.url}: {malicious_results}")
    
            vendor_information = {}
            for result_type, vendors in malicious_results.items():
                for vendor_name in vendors:
                    vendor_info = await self.get_vendor_information(vendor_name)
                    vendor_information[vendor_name] = vendor_info
            
           
            focal_points = await self.get_entity_focal_points(platform)
            
            details = json.dumps({
                "scan_date": scan_result.get("_metadata", {}).get("scan_date"),
                "malicious_results": malicious_results,
                "vendor_information": vendor_information
            })
            
            public_template = await sync_to_async(render_to_string)(
                'VirusTotalAlertPublic.html',
                {
                    "site_url": platform.url,
                    "entity_name": platform.entity.name,
                    "scan_date": scan_result.get("_metadata", {}).get("scan_date"),
                    "points_focaux": focal_points
                }
            )
            
            await self.create_alert(platform, details, public_template, malicious_results)
            
            if self.can_receive_email:
                admin_template = await sync_to_async(render_to_string)(
                    'VirusTotalAlert.html',
                    {
                        "site_url": platform.url,
                        "entity_name": platform.entity.name,
                        "scan_date": scan_result.get("_metadata", {}).get("scan_date"),
                        "malicious_results": malicious_results,
                        "vendor_information": vendor_information,
                        "points_focaux": focal_points
                    }
                )
                
                from apps.mail_setting.tasks import send_email_task
                send_email_task.delay(
                    subject=f"Oju Alert: VirusTotal Detection for {platform.url}",
                    body=admin_template,
                    to_recipients=[self.receive_email],
                    is_html=True
                )
            
            logger.info(f"VirusTotal scan completed for {platform.url} with alerts created")
            
        except (APIKeyError, NetworkError, RateLimitError, ScanError, 
                ResourceNotFoundError, ValidationError, ConfigurationError, 
                AnalysisError, TimeoutError, AuthenticationError, 
                PermissionError, ServiceUnavailableError) as e:
            logger.error(f"VirusTotal scanning error for {platform.url}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error scanning {platform.url}: {str(e)}", exc_info=True)
    
    async def run(self) -> None:
        """Run the VirusTotal scanning task."""
        logger.info("Starting VirusTotal scan task")
        
        try:
            init_successful = await self.initialize()
            
            if not init_successful:
                logger.error("Initialization failed, aborting scan")
                return
            
            logger.info(f"Starting VirusTotal scanning with {self.max_workers} workers")
            
            if not self.platforms:
                logger.warning("No active platforms found to scan")
                return
            
            # semaphore = asyncio.Semaphore(self.max_workers)
            
            # async def scan_platform_with_semaphore(platform):
            #     async with semaphore:
            #         await self.scan_platform(platform)
            
            # await asyncio.gather(*[scan_platform_with_semaphore(platform) for platform in self.platforms])

            for platform in self.platforms:
                await self.scan_platform(platform)
                await asyncio.sleep(3)
            
            logger.info("VirusTotal scanning completed successfully")
            
        except Exception as e:
            logger.error(f"Error during VirusTotal scanning: {str(e)}", exc_info=True)
        finally:
            if self.scanner:
                try:
                    await self.scanner.close()
                except Exception as e:
                    logger.warning(f"Error closing VirusTotal scanner: {str(e)}")
            
            logger.info("VirusTotal scan task completed")

