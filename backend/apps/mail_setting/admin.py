from django.contrib import admin
from django.utils.html import format_html
from .models import MailConfig

@admin.register(MailConfig)
class MailConfigAdmin(admin.ModelAdmin):
    list_display = ('smtp_server', 'email_host', 'is_active')
    list_filter = ('is_active', 'use_tls', 'use_ssl')
    search_fields = ('smtp_server', 'email_host')
    readonly_fields = ('id', 'created_at', 'updated_at')

    fieldsets = (
        ('Server Configuration', {
            'fields': (
                'smtp_server',
                'smtp_port',
                ('use_tls', 'use_ssl'),
            )
        }),
        ('Authentication', {
            'fields': (
                'email_host',
            )
        }),
        ('Email Settings', {
            'fields': (
                'default_sender_name',
                'default_reply_to',
                'is_active',
            )
        }),
        ('Metadata', {
            'classes': ('collapse',),
            'fields': ('id', 'created_at', 'updated_at')
        })
    )


    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        success, message = obj.test_connection()
        if not success:
            self.message_user(request, f"Configuration saved but test failed: {message}", level='WARNING')

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False 