from django.http import HttpResponse
from django.shortcuts import redirect


def restrict_access(allowed_users=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.groups.exists():
                user_groups = request.user.groups.values_list('name',flat=True)
                if 'admin' in user_groups or any(group in allowed_users for group in user_groups):
                    return view_func(request, *args, **kwargs) 
            return redirect('account_login')
        return wrapper_func
    return decorator