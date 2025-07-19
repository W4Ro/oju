from django.core.management.base import BaseCommand
from ...models import MailConfig

class Command(BaseCommand):
    help = 'Initialize mail configuration with default values'

    def handle(self, *args, **kwargs):
        if MailConfig.objects.exists():
            self.stdout.write(
                self.style.WARNING('Mail configuration already exists')
            )
            return

        default_config = MailConfig.objects.create(
            smtp_server='smtp.example.com',
            smtp_port=587,
            use_tls=False,
            use_ssl=False,
            email_host='noreply@example.com',
            email_password='default_password_change_me',
            default_sender_name='System Mailer',
            default_reply_to='noreply@example.com',
            is_active=False
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created mail configuration with ID: {default_config.id}'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                'Please update the configuration with your actual SMTP settings'
            )
        )