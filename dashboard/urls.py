from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # These will be implemented in Phase 5
    path('', views.dashboard_home, name='home'),
]