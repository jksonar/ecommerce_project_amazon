from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    # Existing seller management URLs
    path('sellers/', views.manage_sellers, name='manage_sellers'),
    path('sellers/<int:seller_id>/', views.seller_detail, name='seller_detail'),
    path('sellers/<int:seller_id>/approve/', views.approve_seller, name='approve_seller'),
    path('sellers/<int:seller_id>/reject/', views.reject_seller, name='reject_seller'),
    
    # New product management URLs
    path('products/', views.manage_products, name='manage_products'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/<int:product_id>/toggle-feature/', views.toggle_product_feature, name='toggle_product_feature'),
    
    # New category management URLs
    path('categories/', views.manage_categories, name='manage_categories'),
    path('categories/add/', views.add_category, name='add_category'),
    
    # New order management URLs
    path('orders/', views.manage_orders, name='manage_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    
    # New user management URLs
    path('users/', views.manage_users, name='manage_users'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
]