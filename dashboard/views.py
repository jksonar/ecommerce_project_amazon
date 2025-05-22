from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def dashboard_home(request):
    # This will be implemented in Phase 5
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'dashboard/access_denied.html')
    
    return render(request, 'dashboard/home.html')

# Create your views here.
