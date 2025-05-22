from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # These will be implemented in Phase 3
    path('checkout/', views.checkout, name='checkout'),
]