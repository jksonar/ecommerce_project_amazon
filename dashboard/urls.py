from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('sellers/', views.manage_sellers, name='manage_sellers'),
    path('sellers/<int:seller_id>/', views.seller_detail, name='seller_detail'),
    path('sellers/<int:seller_id>/approve/', views.approve_seller, name='approve_seller'),
    path('sellers/<int:seller_id>/reject/', views.reject_seller, name='reject_seller'),
]