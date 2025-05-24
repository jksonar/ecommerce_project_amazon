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
    from orders.models import OrderItem
    order_items = OrderItem.objects.filter(product__seller=seller).select_related('order', 'product')
    
    # Calculate revenue
    revenue = sum(item.get_total_price() for item in order_items if item.order.status == 'C')
    
    context = {
        'seller': seller,
        'products': products[:5],  # Show only 5 most recent products
        'orders': order_items[:5],  # Show only 5 most recent orders
        'total_products': products.count(),
        'total_orders': order_items.count(),
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
            images = request.FILES.getlist('image')
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
