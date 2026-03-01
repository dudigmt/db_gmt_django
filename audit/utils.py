from .models import AuditLog

def log_action(request, action, description="", data=None):
    """Utility function untuk mencatat aksi user"""
    user = request.user if request.user.is_authenticated else None
    
    # Dapatkan IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    
    AuditLog.objects.create(
        user=user,
        action=action,
        description=description,
        ip_address=ip,
        data=data or {}
    )