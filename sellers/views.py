from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def seller_register(request):
    # This will be implemented in Phase 5
    messages.info(request, 'This feature will be available soon!')
    return render(request, 'sellers/register.html')

@login_required
def seller_dashboard(request):
    # This will be implemented in Phase 5
    if not request.user.is_seller:
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'sellers/access_denied.html')
    
    return render(request, 'sellers/dashboard.html')

# Create your views here.
