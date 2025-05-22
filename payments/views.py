from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def checkout(request):
    # This will be implemented in Phase 3
    messages.info(request, 'This feature will be available soon!')
    return render(request, 'payments/checkout.html')

# Create your views here.
