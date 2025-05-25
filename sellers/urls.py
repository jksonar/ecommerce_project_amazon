from django.urls import path
from . import views

app_name = 'sellers'

urlpatterns = [
    path('register/', views.seller_register, name='register'),
    path('dashboard/', views.seller_dashboard, name='dashboard'),
    path('products/', views.seller_products, name='products'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    # Order management URLs
    path('orders/', views.seller_orders, name='orders'),
    path('orders/<int:order_id>/', views.seller_order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    # New analytics URL
    path('analytics/', views.seller_analytics, name='analytics'),
]