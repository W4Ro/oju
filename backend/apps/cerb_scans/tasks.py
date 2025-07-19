from celery import shared_task
import asyncio
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

def run_async_monitoring(monitoring):
    """
    run_async_monitoring runs the monitoring process in an asyncio event loop.
    This function is designed to be called from a Celery task to ensure that
    the monitoring process runs asynchronously without blocking the main thread.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(monitoring.run())
    finally:
        loop.close()

@shared_task(bind=True, name='apps.cerb_scans.tasks.run_monitoring')
def run_monitoring(self):
    """
    Celery task to run monitoring
    """
    from .monitoring import Monitoring 
    
    task_id = self.request.id
    lock_id = f"monitoring_task_lock"
    lock_expire = 60 * 60 * 6 # 24 hours

    acquired = cache.add(lock_id, task_id, lock_expire)
    if not acquired:
        current_task_id = cache.get(lock_id)
        logger.info(f"Monitoring task already running with ID: {current_task_id}, skipping this execution (task_id: {task_id})")
        return {
            'status': 'skipped',
            'message': 'Another monitoring task already running',
            'task_id': task_id
        }

    logger.info(f"Starting monitoring task (task_id: {task_id})")
    
    try:
        
        monitoring = Monitoring()
        
        run_async_monitoring(monitoring)
        
        logger.info(f"Monitoring task completed successfully (task_id: {task_id})")
        return {
            'status': 'success',
            'message': 'Monitoring completed successfully',
            'task_id': task_id
        }
        
    except Exception as e:
        logger.error(f"Error during monitoring task: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'message': f"Error during monitoring: {str(e)}",
            'task_id': task_id
        }
    finally:
        cache.delete(lock_id)
        logger.info(f"Monitoring task lock released (task_id: {task_id})")