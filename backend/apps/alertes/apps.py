from django.apps import AppConfig


class AlertesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.alertes'
    
    def ready(self):
        import apps.alertes.signals