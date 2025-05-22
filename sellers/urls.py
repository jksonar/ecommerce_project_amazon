from django.urls import path
from . import views

app_name = 'sellers'

urlpatterns = [
    # These will be implemented in Phase 5
    path('register/', views.seller_register, name='register'),
    path('dashboard/', views.seller_dashboard, name='dashboard'),
]