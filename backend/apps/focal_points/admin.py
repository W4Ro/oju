from django.contrib import admin
from .models import FocalPoint, FocalFunction

@admin.register(FocalFunction)
class FocalFunctionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('name',)

    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False  

@admin.register(FocalPoint)
class FocalPointAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'function', 'email', 'phone_number', 'is_active')
    list_filter = ('function', 'is_active', 'created_at')
    search_fields = ('full_name', 'email', 'phone_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('function', 'full_name')

    fieldsets = (
        (None, {
            'fields': ('full_name', 'function')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_number')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False  