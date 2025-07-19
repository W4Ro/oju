from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, PasswordReset, BlacklistedToken

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'nom_prenom', 'role', 'is_active', 'created_at')
    list_filter = ('is_active', 'role', 'created_at')
    search_fields = ('email', 'username', 'nom_prenom')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('username', 'nom_prenom')}),
        (_('Permissions'), {
            'fields': ('role', 'is_active'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'nom_prenom', 'password1', 'password2', 'role'),
        }),
    )
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False 

@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_used', 'attempts', 'expires_at', 'created_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__email', 'token')
    readonly_fields = ('created_at',)

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False 

@admin.register(BlacklistedToken)
class BlacklistedTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'blacklisted_at')
    list_filter = ('blacklisted_at',)
    search_fields = ('user__email', 'token')
    readonly_fields = ('blacklisted_at',)

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False 