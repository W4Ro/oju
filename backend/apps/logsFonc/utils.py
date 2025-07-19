from .models import SystemLog

def create_system_log(name, details=None):
    return SystemLog.objects.create(
        user=name,
        details=details
    )