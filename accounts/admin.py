from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['id', 'created_at', 'updated_at']

admin.site.register(User, UserAdmin)
