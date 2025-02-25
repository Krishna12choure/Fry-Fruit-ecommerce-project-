from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test

def admin_required(view_func):
    """
    This decorator ensures that only users who are superusers (admins) can access the view.
    Allows non-authenticated users to access the login page.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:  # If the user is authenticated
            if not request.user.is_superuser:  # If the user is not an admin
                return redirect('home')  # Redirect to home or any page of your choice
        return view_func(request, *args, **kwargs)  # Allow access to the view

    return _wrapped_view
