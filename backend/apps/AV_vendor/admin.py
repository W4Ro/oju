from django.contrib import admin
from .models import AVVendor

@admin.register(AVVendor)
class AVVendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'contact', 'comments')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('name',)

    fieldsets = (
        (None, {
            'fields': ('name', 'contact')
        }),
        ('Additional Information', {
            'fields': ('comments',)
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