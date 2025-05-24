from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from .models import Review
from .forms import ReviewForm

@login_required
def add_review(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    
    # Check if user already reviewed this product
    existing_review = Review.objects.filter(user=request.user, product=product).first()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            
            if existing_review:
                messages.success(request, 'Your review has been updated!')
            else:
                messages.success(request, 'Your review has been added!')
            
            return redirect('products:product_detail', slug=product_slug)
    else:
        form = ReviewForm(instance=existing_review)
    
    context = {
        'form': form,
        'product': product,
        'existing_review': existing_review
    }
    return render(request, 'reviews/add_review.html', context)

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_slug = review.product.slug
    
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Your review has been deleted!')
        return redirect('products:product_detail', slug=product_slug)
    
    context = {
        'review': review
    }
    return render(request, 'reviews/delete_review.html', context)
# Create your views here.
