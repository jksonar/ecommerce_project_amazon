from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from products.models import Product
from .models import Cart, CartItem, Order
from decimal import Decimal

@login_required
def cart_view(request):
    # Get or create cart for the user
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    # Calculate totals
    cart_total = sum(item.total_price for item in cart_items)
    tax = Decimal('0.10') * cart_total  # 10% tax
    total = cart_total + tax
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'tax': tax,
        'total': total,
    }
    
    return render(request, 'orders/cart.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Check if product already in cart
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    # If product already exists in cart, increase quantity
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f'Added another {product.name} to your cart.')
    else:
        messages.success(request, f'{product.name} has been added to your cart.')
    
    # Redirect based on where the request came from
    next_url = request.GET.get('next', 'orders:cart')
    return redirect(next_url)

@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    action = request.POST.get('action')
    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, 'Cart updated.')
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
        messages.success(request, 'Cart updated.')
    elif action == 'remove':
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')
    
    return redirect('orders:cart')

@login_required
def order_confirmation(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        return render(request, 'orders/order_confirmation.html', {'order': order})
    except Order.DoesNotExist:
        raise Http404("Order not found")

@login_required
def order_detail(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        
        # Calculate subtotal and tax
        subtotal = sum(item.total_price for item in order.items.all())
        tax = order.total_amount - subtotal
        
        context = {
            'order': order,
            'subtotal': subtotal,
            'tax': tax,
        }
        
        return render(request, 'orders/order_detail.html', context)
    except Order.DoesNotExist:
        raise Http404("Order not found")
# Create your views here.
