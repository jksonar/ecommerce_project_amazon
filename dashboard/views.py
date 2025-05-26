from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from sellers.models import Seller
from django.core.mail import send_mail
from django.conf import settings

@login_required
def dashboard_home(request):
    # Check if user is staff
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'dashboard/access_denied.html')
    
    # Get counts for dashboard statistics
    from products.models import Product
    from orders.models import Order
    from accounts.models import User
    
    product_count = Product.objects.count()
    order_count = Order.objects.count()
    user_count = User.objects.count()
    pending_sellers = Seller.objects.filter(status='P').count()
    
    context = {
        'product_count': product_count,
        'order_count': order_count,
        'user_count': user_count,
        'pending_sellers': pending_sellers
    }
    
    return render(request, 'dashboard/home.html', context)

@login_required
def manage_sellers(request):
    # Check if user is staff
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'dashboard/access_denied.html')
    
    # Get all sellers
    sellers = Seller.objects.all().order_by('-created_at')
    
    return render(request, 'dashboard/manage_sellers.html', {'sellers': sellers})

@login_required
def seller_detail(request, seller_id):
    # Check if user is staff
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'dashboard/access_denied.html')
    
    # Get seller
    seller = get_object_or_404(Seller, id=seller_id)
    
    return render(request, 'dashboard/seller_detail.html', {'seller': seller})

@login_required
def approve_seller(request, seller_id):
    # Check if user is staff
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'dashboard/access_denied.html')
    
    # Get seller
    seller = get_object_or_404(Seller, id=seller_id)
    
    if request.method == 'POST':
        # Update seller status
        seller.status = 'A'  # Approved
        seller.save()
        
        # Send email notification to seller
        send_mail(
            'Your Seller Application has been Approved',
            f'Congratulations! Your seller application for {seller.company_name} has been approved. You can now start selling products on our platform.',
            settings.DEFAULT_FROM_EMAIL,
            [seller.user.email],
            fail_silently=False,
        )
        
        # Create notification for seller
        from dashboard.models import Notification
        Notification.objects.create(
            user=seller.user,
            notification_type='A',
            title='Seller Application Approved',
            message='Your seller application has been approved. You can now start selling products on our platform.'
        )
        
        messages.success(request, f'Seller {seller.company_name} has been approved.')
        return redirect('dashboard:manage_sellers')
    
    return render(request, 'dashboard/approve_seller.html', {'seller': seller})

@login_required
def reject_seller(request, seller_id):
    # Check if user is staff
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'dashboard/access_denied.html')
    
    # Get seller
    seller = get_object_or_404(Seller, id=seller_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        # Update seller status
        seller.status = 'R'  # Rejected
        seller.save()
        
        # Send email notification to seller
        send_mail(
            'Your Seller Application has been Rejected',
            f'We regret to inform you that your seller application for {seller.company_name} has been rejected.\n\nReason: {reason}\n\nIf you have any questions, please contact our support team.',
            settings.DEFAULT_FROM_EMAIL,
            [seller.user.email],
            fail_silently=False,
        )
        
        # Create notification for seller
        from dashboard.models import Notification
        Notification.objects.create(
            user=seller.user,
            notification_type='A',
            title='Seller Application Rejected',
            message=f'Your seller application has been rejected. Reason: {reason}'
        )
        
        messages.success(request, f'Seller {seller.company_name} has been rejected.')
        return redirect('dashboard:manage_sellers')
    
    return render(request, 'dashboard/reject_seller.html', {'seller': seller})

@login_required
def manage_users(request):
    # Check if user is staff
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'dashboard/access_denied.html')
    
    # Get all users
    users = User.objects.all().order_by('-date_joined')
    
    return render(request, 'dashboard/manage_users.html', {'users': users})

@login_required
def user_detail(request, user_id):
    # Check if user is staff
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'dashboard/access_denied.html')
    
    # Get user
    user = get_object_or_404(User, id=user_id)
    
    # Get user's orders
    orders = Order.objects.filter(user=user).order_by('-created_at')
    
    # Get user's addresses
    addresses = Address.objects.filter(user=user)
    
    return render(request, 'dashboard/user_detail.html', {
        'user_detail': user,
        'orders': orders,
        'addresses': addresses
    })

@login_required
def manage_products(request):
    # Check if user is staff
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'dashboard/access_denied.html')
    
    # Get all products
    products = Product.objects.all().order_by('-created_at')
    
    return render(request, 'dashboard/manage_products.html', {'products': products})

@login_required
def product_detail(request, product_id):
    # Check if user is staff
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'dashboard/access_denied.html')
    
    # Get product
    product = get_object_or_404(Product, id=product_id)
    
    return render(request, 'dashboard/product_detail.html', {'product': product})

@login_required
def toggle_product_feature(request, product_id):
    # Check if user is staff
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'dashboard/access_denied.html')
    
    # Get product
    product = get_object_or_404(Product, id=product_id)
    
    # Toggle featured status
    product.featured = not product.featured
    product.save()
    
    messages.success(request, f'Product "{product.name}" is now {"featured" if product.featured else "not featured"}.')
    return redirect('dashboard:product_detail', product_id=product.id)


@login_required
def manage_categories(request):
    # Check if user is staff
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'dashboard/access_denied.html')
    
    # Get all categories
    categories = Category.objects.all().order_by('name')
    
    return render(request, 'dashboard/manage_categories.html', {'categories': categories})

@login_required
def add_category(request):
    # Check if user is staff
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'dashboard/access_denied.html')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        parent_id = request.POST.get('parent')
        
        if not name:
            messages.error(request, 'Category name is required.')
            return redirect('dashboard:add_category')
        
        # Create slug from name
        from django.utils.text import slugify
        slug = slugify(name)
        
        # Check if category with this slug already exists
        if Category.objects.filter(slug=slug).exists():
            messages.error(request, f'Category with name "{name}" already exists.')
            return redirect('dashboard:add_category')
        
        # Create category
        category = Category(name=name, description=description, slug=slug)
        
        # Set parent if provided
        if parent_id:
            try:
                parent = Category.objects.get(id=parent_id)
                category.parent = parent
            except Category.DoesNotExist:
                pass
        
        category.save()
        messages.success(request, f'Category "{name}" has been added.')
        return redirect('dashboard:manage_categories')
    
    # Get all categories for parent selection
    categories = Category.objects.all().order_by('name')
    
    return render(request, 'dashboard/add_category.html', {'categories': categories})

@login_required
def manage_orders(request):
    # Check if user is staff
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'dashboard/access_denied.html')
    
    # Get all orders
    orders = Order.objects.all().order_by('-created_at')
    
    return render(request, 'dashboard/manage_orders.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    # Check if user is staff
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return render(request, 'dashboard/access_denied.html')
    
    # Get order
    order = get_object_or_404(Order, id=order_id)
    
    # Get order items
    order_items = order.items.all().select_related('product')
    
    return render(request, 'dashboard/order_detail.html', {
        'order': order,
        'order_items': order_items
    })
