from celery import shared_task
from .models import Cerebrate, RTIR
from django.utils import timezone
from .cerebrate import CerebrateAPI
from .rtir import RTIRClient
from typing import Dict, List, Optional, Union
from .scan_vt import VirusTotalTask
import asyncio

import logging
logger = logging.getLogger(__name__)

@shared_task(bind=False, name="apps.tools_integrated.tasks.virustotal_scan")
def virustotal_scan():
    """
    Celery task function that runs the VirusTotal scanning.
    
    This is the entry point for the scheduled task.
    """
    try:
        logger.info("Starting VirusTotal scan Celery task")
        task = VirusTotalTask()
        asyncio.run(task.run())
        logger.info("VirusTotal scan Celery task completed")
    except Exception as e:
        logger.error(f"Error in VirusTotal scan Celery task: {str(e)}", exc_info=True)

@shared_task(bind=False, name="apps.tools_integrated.tasks.refresh_cerebrate")
def refresh_cerebrate():
    try:
        cerebrate = Cerebrate.objects.first()
        if not cerebrate:
            logger.critical("Cerebrate config has not been find")
            return False, "No config has been find"
        if not cerebrate.is_active:
            logger.critical("Cerebrate is not active")
            return False, "Cerebrate is not active"

        api = CerebrateAPI(cerebrate.url, cerebrate.api_key)
        if api.check_connection():
            api.sync_from_cerebrate()
       
            cerebrate.updated_at = timezone.now()
            cerebrate.save(update_fields=['updated_at'])
    except Exception as e:
        logger.error(f"Error while refreshing: {str(e)}")

@shared_task(bind=True, max_retries=3)
def create_rtir_ticket(
    self,
    subject: str,
    content: str,
    requestors: List[str],
    queue: str = "Incident Reports",
    cc: Optional[List[str]] = None,
    admin_cc: Optional[List[str]] = None,
    priority: str = "Normal",
    ip: Optional[str] = None,
    domain: Optional[str] = None,
    cve_id: Optional[str] = None,
    reporter_type: Optional[str] = None,
    status: str = "new"
) -> Dict[str, Union[str, bool]]:
    try:
        logger.info(f"Starting RTIR ticket creation: {subject}")
        rtir_conf = RTIR.objects.first()
        if not rtir_conf.is_active:
            logger.critical(f"attemps to create ticket about {subject}, but RTIR is not active")
            return
        
        rtir = RTIRClient(
            rtir_conf.url,
            rtir_conf.username,
            rtir_conf.password
        )
        
        
        if not rtir.authenticate():
            error_msg = "Failed to authenticate to RTIR"
            logger.error(error_msg)
            raise Exception(error_msg)
            
        result = rtir.create_ticket(
            queue=queue,
            subject=subject,
            content=content,
            requestors=requestors,
            cc=cc,
            admin_cc=admin_cc,
            priority=priority,
            ip=ip,
            domain=domain,
            cve_id=cve_id,
            reporter_type=reporter_type,
            status=status
        )
        
        if result['success']:
            logger.info(f"RTIR ticket created successfully: {subject}")
        else:
            logger.error(f"Failed to create RTIR ticket: {result.get('error')}")
            
        return result
        
    except Exception as e:
        logger.error(f"Error creating RTIR ticket about {subject}: {str(e)}")
        raise

