from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # These will be implemented in Phase 4
    path('add/<slug:product_slug>/', views.add_review, name='add_review'),
]