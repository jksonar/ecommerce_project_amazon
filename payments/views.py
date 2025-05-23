from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from orders.models import Cart, Order, OrderItem
from accounts.models import Address
from .models import Payment
from decimal import Decimal
import stripe
import uuid

# Initialize Stripe with your secret key
# In production, use environment variables for sensitive keys
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def checkout(request):
    # Get user's cart
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        
        if not cart_items.exists():
            messages.warning(request, 'Your cart is empty.')
            return redirect('orders:cart')
            
        # Calculate totals
        cart_total = sum(item.total_price for item in cart_items)
        tax = Decimal('0.10') * cart_total  # 10% tax
        total = cart_total + tax
        
        # Get user's addresses
        addresses = Address.objects.filter(user=request.user)
        
        # Create Stripe payment intent for client-side processing
        intent = None
        client_secret = None
        
        if request.method == 'POST':
            # Create a PaymentIntent with the order amount and currency
            try:
                intent = stripe.PaymentIntent.create(
                    amount=int(total * 100),  # Convert to cents
                    currency='usd',
                    metadata={'integration_check': 'accept_a_payment'},
                )
                client_secret = intent.client_secret
            except Exception as e:
                messages.error(request, f"Stripe error: {str(e)}")
        
        context = {
            'cart_items': cart_items,
            'cart_total': cart_total,
            'tax': tax,
            'total': total,
            'addresses': addresses,
            'client_secret': client_secret,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        }
        
        return render(request, 'payments/checkout.html', context)
        
    except Cart.DoesNotExist:
        messages.warning(request, 'Your cart is empty.')
        return redirect('orders:cart')

@login_required
def place_order(request):
    if request.method == 'POST':
        # Get user's cart
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.items.all()
            
            if not cart_items.exists():
                messages.warning(request, 'Your cart is empty.')
                return redirect('orders:cart')
                
            # Get selected address
            address_id = request.POST.get('shipping_address')
            if not address_id:
                messages.error(request, 'Please select a shipping address.')
                return redirect('payments:checkout')
                
            try:
                address = Address.objects.get(id=address_id, user=request.user)
            except Address.DoesNotExist:
                messages.error(request, 'Invalid shipping address.')
                return redirect('payments:checkout')
                
            # Calculate totals
            cart_total = sum(item.total_price for item in cart_items)
            tax = Decimal('0.10') * cart_total  # 10% tax
            total = cart_total + tax
            
            # Get payment method
            payment_method = request.POST.get('payment_method', 'C')  # Default to Credit Card
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                address=address,
                total_amount=total,
                payment_status=False  # Will be updated after payment confirmation
            )
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price if not cart_item.product.discount_price else cart_item.product.discount_price
                )
            
            # Process payment
            payment_intent_id = request.POST.get('payment_intent_id')
            
            if payment_intent_id:
                try:
                    # Confirm the payment intent
                    intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                    
                    # Create payment record
                    payment = Payment.objects.create(
                        order=order,
                        payment_method=payment_method,
                        transaction_id=payment_intent_id,
                        amount=total,
                        status='C' if intent.status == 'succeeded' else 'P'
                    )
                    
                    # Update order payment status
                    if intent.status == 'succeeded':
                        order.payment_status = True
                        order.status = 'C'  # Confirmed
                        order.save()
                        
                        # Clear cart
                        cart_items.delete()
                        
                        messages.success(request, 'Your order has been placed and payment processed successfully!')
                        return redirect('orders:order_confirmation', order_id=order.id)
                    else:
                        messages.warning(request, 'Payment is being processed. We will update your order status soon.')
                        return redirect('orders:order_confirmation', order_id=order.id)
                        
                except stripe.error.StripeError as e:
                    # Handle Stripe errors
                    messages.error(request, f"Payment error: {str(e)}")
                    order.status = 'X'  # Cancelled
                    order.save()
                    return redirect('payments:checkout')
            else:
                # For cash on delivery or other non-Stripe methods
                Payment.objects.create(
                    order=order,
                    payment_method=payment_method,
                    transaction_id=f"COD-{uuid.uuid4().hex[:8].upper()}",
                    amount=total,
                    status='P'  # Pending
                )
                
                # Clear cart
                cart_items.delete()
                
                messages.success(request, 'Your order has been placed successfully! Payment will be collected upon delivery.')
                return redirect('orders:order_confirmation', order_id=order.id)
                
        except Cart.DoesNotExist:
            messages.warning(request, 'Your cart is empty.')
            return redirect('orders:cart')
    
    return redirect('payments:checkout')

@login_required
def payment_success(request):
    order_id = request.GET.get('order_id')
    if order_id:
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            return render(request, 'payments/payment_success.html', {'order': order})
        except Order.DoesNotExist:
            pass
    return redirect('accounts:profile')

@login_required
def payment_cancel(request):
    return render(request, 'payments/payment_cancel.html')
