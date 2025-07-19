from django.core.cache import cache
from apps.users.models import User

def str_exception(exc):
    if hasattr(exc, 'detail') and isinstance(exc.detail, dict):
        first_error = next(iter(exc.detail.values()), None)
        if isinstance(first_error, list) and first_error:
            return first_error[0]
    return str(exc.args[0]) if exc.args else "error"

def assignment_check(allowed_fields, request_data):
    
    data = {
            key: value for key, value in request_data 
            if key in allowed_fields
        }
    for field in allowed_fields:
        if field not in data:
            return True, f"Fields {field} is required"
        if data.get(field) is None or (isinstance(data.get(field), (str, dict, list)) and not data.get(field)):
            return True, f"Fields {field} is required"
    return False, data

def assign_user(email):
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None
    
