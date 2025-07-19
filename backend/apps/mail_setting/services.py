# apps/mail_settings/services.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
from typing import List, Optional, Dict, Union
import base64
from django.core.files.base import ContentFile
from .models import MailConfig, EmailLog
from django.utils import timezone

class EmailService:
    def __init__(self):
        self.config = MailConfig.objects.filter(is_active=True).first()
        if not self.config:
            raise ValueError("No active mail configuration found")

    def _create_message(
        self,
        subject: str,
        body: str,
        to_recipients: List[str],
        cc_recipients: Optional[List[str]] = None,
        bcc_recipients: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, str]]] = None,
        is_html: bool = False
    ) -> MIMEMultipart:
        """Create an email message with all the necessary components"""
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = f"{self.config.default_sender_name} <{self.config.email_host}>"
        msg['To'] = ', '.join(to_recipients)
        
        if cc_recipients:
            msg['Cc'] = ', '.join(cc_recipients)
        
        if self.config.default_reply_to:
            msg['Reply-To'] = self.config.default_reply_to

        content_type = 'html' if is_html else 'plain'
        msg.attach(MIMEText(body, content_type))

        if attachments:
            for attachment in attachments:
                filename = attachment['filename']
                content = base64.b64decode(attachment['content'])
                
                part = MIMEApplication(content, Name=filename)
                part['Content-Disposition'] = f'attachment; filename="{filename}"'
                msg.attach(part)

        return msg

    def send_email(
        self,
        subject: str,
        body: str,
        to_recipients: List[str],
        cc_recipients: Optional[List[str]] = None,
        bcc_recipients: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, str]]] = None,
        is_html: bool = False
    ) -> EmailLog:
        """
            Sends an email and logs it

            Args:
                subject: Subject of the email
                body: Body of the email
                to_recipients: List of primary recipients
                cc_recipients: List of recipients in copy
                bcc_recipients: List of recipients in blind copy
                attachments: List of attachments in the format
                [{'filename': 'name.ext', 'content': 'base64_content'}]
                is_html: If True, the body is treated as HTML
        """
        email_log = EmailLog.objects.create(
            subject=subject,
            to_recipients=to_recipients,
            cc_recipients=cc_recipients or [],
            bcc_recipients=bcc_recipients or [],
            body=body,
            is_html=is_html,
            attachments=attachments or []
        )

        try:
            msg = self._create_message(
                subject,
                body,
                to_recipients,
                cc_recipients,
                bcc_recipients,
                attachments,
                is_html
            )

            
            smtp_class = smtplib.SMTP_SSL if self.config.use_ssl else smtplib.SMTP
            with smtp_class(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                
                server.login(self.config.email_host, self.config.email_password)

                to_recipients = [to_recipients] if isinstance(to_recipients, str) else to_recipients
                cc_recipients = cc_recipients or []
                bcc_recipients = bcc_recipients or []

                all_recipients = to_recipients + cc_recipients + bcc_recipients

                server.sendmail(
                    self.config.email_host,
                    all_recipients,
                    msg.as_string()
                )

           
            email_log.status = EmailLog.EmailStatus.SENT
            email_log.sent_at = timezone.now()
            email_log.save()

        except Exception as e:
            email_log.status = EmailLog.EmailStatus.FAILED
            email_log.error_message = str(e)
            email_log.save()
            raise

        return email_log
