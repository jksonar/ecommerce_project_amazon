from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def cart_view(request):
    # This will be implemented in Phase 2
    return render(request, 'orders/cart.html')

@login_required
def add_to_cart(request, product_id):
    # This will be implemented in Phase 2
    messages.info(request, 'This feature will be available soon!')
    return redirect('products:product_list')

# Create your views here.
