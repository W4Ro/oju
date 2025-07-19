from celery import shared_task
from typing import List, Optional, Dict
from .services import EmailService

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,
    autoretry_for=(Exception,),
    retry_backoff=True
)
def send_email_task(
    self,
    subject: str,
    body: str,
    to_recipients: List[str],
    cc_recipients: Optional[List[str]] = None,
    bcc_recipients: Optional[List[str]] = None,
    attachments: Optional[List[Dict[str, str]]] = None,
    is_html: bool = False
) -> str:
    """
    Celery task for sending emails in the background

        Args:
        subject: Subject of the email
        body: Body of the email
        to_recipients: List of primary recipients
        cc_recipients: List of recipients in copy
        bcc_recipients: List of recipients in blind copy
        attachments: List of attachments in the format
        [{'filename': 'name.ext', 'content': 'base64_content'}]
        is_html: If True, the body is treated as HTML

    Returns:
        str: ID of the created email log
    """
    try:
        email_service = EmailService()
        email_log = email_service.send_email(
            subject=subject,
            body=body,
            to_recipients=to_recipients,
            cc_recipients=cc_recipients,
            bcc_recipients=bcc_recipients,
            attachments=attachments,
            is_html=is_html
        )
        return str(email_log.id)
    except Exception as exc:
        self.retry(exc=exc)
