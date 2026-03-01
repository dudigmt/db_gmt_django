from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # SuperAdmin bisa akses semua
            if request.user.profile.role == 'SuperAdmin':
                return view_func(request, *args, **kwargs)
            
            # Cek role lain
            if request.user.profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'You are not authorized to view this page.')
                return redirect('dashboard')
        return wrapper
    return decorator

def admin_only(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if request.user.profile.role in ['SuperAdmin', 'Admin']:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Admin access required.')
            return redirect('dashboard')
    return wrapper