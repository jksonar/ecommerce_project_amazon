from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # These will be implemented in Phase 2
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
]