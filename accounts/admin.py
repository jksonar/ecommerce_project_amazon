from django.contrib import admin
from .models import User, Address

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_seller', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('is_seller', 'is_staff', 'is_active')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_type', 'city', 'country', 'default')
    list_filter = ('address_type', 'default', 'country')
    search_fields = ('user__username', 'street_address', 'city')

# Register your models here.
