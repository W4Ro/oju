from django.core.management.base import BaseCommand
from ...models import FocalFunction
from django.db import transaction

class Command(BaseCommand):
    help = 'Initialize default focal function if it does not exist'

    def handle(self, *args, **kwargs):
        try:
            with transaction.atomic():
                focal_function, created = FocalFunction.objects.get_or_create(
                    name="Default"
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS('Successfully created default focal function')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('Default focal function already exists')
                    )
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating default focal function: {str(e)}')
            )