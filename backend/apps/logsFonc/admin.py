from django.contrib import admin
from .models import SystemLog

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'created_at', 'details')
    list_filter = ('created_at',)
    search_fields = ('user_username', 'details')
    readonly_fields = ('id', 'created_at')
    ordering = ('-created_at',)

    def get_username(self, obj):
        return obj.user.username if obj.user else "N/A"
    get_username.short_description = "User"

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False 