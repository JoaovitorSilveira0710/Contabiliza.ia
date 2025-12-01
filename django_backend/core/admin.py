from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active', 'created_at')
    list_filter = ('role', 'is_staff', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('username', 'password', 'email', 'first_name', 'last_name', 'phone')
        }),
        ('Permissões', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Avatar', {
            'fields': ('avatar',)
        }),
        ('Datas Importantes', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')
        }),
    )
