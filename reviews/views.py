from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def add_review(request, product_slug):
    # This will be implemented in Phase 4
    messages.info(request, 'This feature will be available soon!')
    return redirect('products:product_detail', slug=product_slug)

# Create your views here.
