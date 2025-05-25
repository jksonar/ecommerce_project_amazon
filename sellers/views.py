from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SellerForm
from .models import Seller

@login_required
def seller_register(request):
    # Check if user is already a seller
    if hasattr(request.user, 'seller_profile'):
        messages.info(request, 'You are already registered as a seller.')
        return redirect('sellers:dashboard')
    
    if request.method == 'POST':
        form = SellerForm(request.POST, request.FILES)
        if form.is_valid():
            seller = form.save(commit=False)
            seller.user = request.user
            seller.status = 'P'  # Pending status
            seller.save()
            
            # Update user's is_seller status
            request.user.is_seller = True
            request.user.save()
            
            # Send notification to admin about new seller application
            from dashboard.models import Notification
            admin_users = User.objects.filter(is_staff=True)
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    notification_type='A',
                    title='New Seller Application',
                    message=f'New seller application from {request.user.username} ({seller.company_name})'
                )
            
            messages.success(request, 'Your seller application has been submitted and is pending approval.')
            return redirect('accounts:profile')
    else:
        form = SellerForm()
    
    return render(request, 'sellers/register.html', {'form': form})

@login_required
def seller_dashboard(request):
    # Check if user is a seller
    if not hasattr(request.user, 'seller_profile'):
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'sellers/access_denied.html')
    
    # Check if seller is approved
    seller = request.user.seller_profile
    if seller.status != 'A':
        messages.warning(request, f'Your seller account is currently {seller.get_status_display()}. You cannot access the full dashboard until approved.')
    
    # Get seller's products
    products = seller.products.all().order_by('-created_at')
    
    # Get seller's orders
    from orders.models import OrderItem, Order
    order_items = OrderItem.objects.filter(product__seller=seller).select_related('order', 'product')
    
    # Get unique orders that contain this seller's products
    orders_with_seller_items = Order.objects.filter(
        items__product__seller=seller
    ).distinct().order_by('-created_at')
    
    # For each order, calculate the seller's portion
    recent_orders = []
    for order in orders_with_seller_items[:5]:  # Get only 5 most recent orders
        # Get only this seller's items in the order
        seller_items = order.items.filter(product__seller=seller)
        
        # Calculate seller's subtotal for this order
        seller_subtotal = sum(item.price * item.quantity for item in seller_items)
        
        recent_orders.append({
            'order': order,
            'seller_items': seller_items,
            'seller_subtotal': seller_subtotal,
        })
    
    # Calculate revenue
    revenue = sum(item.price * item.quantity for item in order_items if item.order.status == 'D')
    
    context = {
        'seller': seller,
        'products': products[:5],  # Show only 5 most recent products
        'recent_orders': recent_orders,  # Show only 5 most recent orders
        'total_products': products.count(),
        'total_orders': orders_with_seller_items.count(),
        'revenue': revenue,
    }
    
    return render(request, 'sellers/dashboard.html', context)

# Add these imports at the top
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import modelformset_factory
from products.models import Product, ProductImage
from products.forms import ProductForm, ProductImageForm, ProductSpecificationFormSet
from .forms import SellerForm
from .models import Seller

# Add these views after the existing views

@login_required
def seller_products(request):
    # Check if user is a seller
    if not hasattr(request.user, 'seller_profile'):
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'sellers/access_denied.html')
    
    seller = request.user.seller_profile
    products = seller.products.all().order_by('-created_at')
    
    return render(request, 'sellers/products.html', {'products': products})

@login_required
def add_product(request):
    # Check if user is a seller
    if not hasattr(request.user, 'seller_profile'):
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'sellers/access_denied.html')
    
    # Check if seller is approved
    seller = request.user.seller_profile
    if seller.status != 'A':
        messages.warning(request, 'Your seller account must be approved before you can add products.')
        return redirect('sellers:dashboard')
    
    if request.method == 'POST':
        form = ProductForm(request.POST)
        image_form = ProductImageForm(request.POST, request.FILES)
        
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = seller
            product.save()
            
            # Handle multiple image uploads
            images = request.FILES.getlist('images')  # Changed from 'image' to 'images'
            for image in images:
                ProductImage.objects.create(product=product, image=image)
            
            # Handle specifications
            spec_formset = ProductSpecificationFormSet(request.POST, instance=product)
            if spec_formset.is_valid():
                spec_formset.save()
            
            messages.success(request, 'Product added successfully!')
            return redirect('sellers:products')
    else:
        form = ProductForm()
        image_form = ProductImageForm()
        spec_formset = ProductSpecificationFormSet()
    
    return render(request, 'sellers/add_product.html', {
        'form': form,
        'image_form': image_form,
        'spec_formset': spec_formset,
    })

@login_required
def edit_product(request, product_id):
    # Check if user is a seller
    if not hasattr(request.user, 'seller_profile'):
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'sellers/access_denied.html')
    
    seller = request.user.seller_profile
    product = get_object_or_404(Product, id=product_id, seller=seller)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        spec_formset = ProductSpecificationFormSet(request.POST, instance=product)
        
        if form.is_valid() and spec_formset.is_valid():
            form.save()
            spec_formset.save()
            
            # Handle image uploads
            images = request.FILES.getlist('image')
            for image in images:
                ProductImage.objects.create(product=product, image=image)
            
            messages.success(request, 'Product updated successfully!')
            return redirect('sellers:products')
    else:
        form = ProductForm(instance=product)
        spec_formset = ProductSpecificationFormSet(instance=product)
    
    return render(request, 'sellers/edit_product.html', {
        'form': form,
        'spec_formset': spec_formset,
        'product': product,
    })

@login_required
def delete_product(request, product_id):
    # Check if user is a seller
    if not hasattr(request.user, 'seller_profile'):
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'sellers/access_denied.html')
    
    seller = request.user.seller_profile
    product = get_object_or_404(Product, id=product_id, seller=seller)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('sellers:products')
    
    return render(request, 'sellers/delete_product.html', {'product': product})


@login_required
def seller_orders(request):
    # Check if user is a seller
    if not hasattr(request.user, 'seller_profile'):
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'sellers/access_denied.html')
    
    # Check if seller is approved
    seller = request.user.seller_profile
    if seller.status != 'A':
        messages.warning(request, 'Your seller account must be approved before you can manage orders.')
        return redirect('sellers:dashboard')
    
    # Get orders containing seller's products
    from django.db.models import Count, Sum, F, Q
    from orders.models import Order, OrderItem
    
    # Get unique orders that contain this seller's products
    orders_with_seller_items = Order.objects.filter(
        items__product__seller=seller
    ).distinct().order_by('-created_at')
    
    # For each order, calculate the seller's portion
    seller_order_data = []
    for order in orders_with_seller_items:
        # Get only this seller's items in the order
        seller_items = order.items.filter(product__seller=seller)
        
        # Calculate seller's subtotal for this order
        seller_subtotal = sum(item.price * item.quantity for item in seller_items)
        
        # Count seller's items in this order
        seller_item_count = seller_items.count()
        
        seller_order_data.append({
            'order': order,
            'seller_items': seller_items,
            'seller_subtotal': seller_subtotal,
            'seller_item_count': seller_item_count
        })
    
    context = {
        'seller_order_data': seller_order_data,
    }
    
    return render(request, 'sellers/orders.html', context)

@login_required
def seller_order_detail(request, order_id):
    # Check if user is a seller
    if not hasattr(request.user, 'seller_profile'):
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'sellers/access_denied.html')
    
    # Check if seller is approved
    seller = request.user.seller_profile
    if seller.status != 'A':
        messages.warning(request, 'Your seller account must be approved before you can manage orders.')
        return redirect('sellers:dashboard')
    
    # Get the order
    from orders.models import Order
    order = get_object_or_404(Order, id=order_id)
    
    # Get only this seller's items in the order
    seller_items = order.items.filter(product__seller=seller)
    
    # Check if the seller has items in this order
    if not seller_items.exists():
        messages.error(request, 'You do not have any products in this order.')
        return redirect('sellers:orders')
    
    # Calculate seller's subtotal for this order
    seller_subtotal = sum(item.price * item.quantity for item in seller_items)
    
    context = {
        'order': order,
        'seller_items': seller_items,
        'seller_subtotal': seller_subtotal,
    }
    
    return render(request, 'sellers/order_detail.html', context)

@login_required
def update_order_status(request, order_id):
    # Check if user is a seller
    if not hasattr(request.user, 'seller_profile'):
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'sellers/access_denied.html')
    
    # Check if seller is approved
    seller = request.user.seller_profile
    if seller.status != 'A':
        messages.warning(request, 'Your seller account must be approved before you can manage orders.')
        return redirect('sellers:dashboard')
    
    # Get the order
    from orders.models import Order
    order = get_object_or_404(Order, id=order_id)
    
    # Get only this seller's items in the order
    seller_items = order.items.filter(product__seller=seller)
    
    # Check if the seller has items in this order
    if not seller_items.exists():
        messages.error(request, 'You do not have any products in this order.')
        return redirect('sellers:orders')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES).keys():
            # Update the order status
            order.status = new_status
            order.save()
            
            # Add a notification for the customer
            from dashboard.models import Notification
            Notification.objects.create(
                user=order.user,
                notification_type='O',  # Order notification
                title='Order Status Updated',
                message=f'Your order #{order.id} status has been updated to {order.get_status_display()}.'
            )
            
            messages.success(request, f'Order status updated to {order.get_status_display()}.')
        else:
            messages.error(request, 'Invalid status selected.')
    
    return redirect('sellers:order_detail', order_id=order_id)
