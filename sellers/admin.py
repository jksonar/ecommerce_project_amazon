from django.contrib import admin
from .models import Seller

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('company_name', 'user__username', 'user__email')
