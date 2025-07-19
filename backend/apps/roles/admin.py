from django.contrib import admin
from django.utils.html import format_html
from .models import Role, Permission, RolePermission

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('permission_code', 'feature_name', 'permission_name', 'description')
    list_filter = ('feature_name',)
    search_fields = ('permission_code', 'feature_name', 'permission_name')
    ordering = ('feature_name', 'permission_name')
    readonly_fields = ('id',)
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False 

class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 1
    autocomplete_fields = ['permission']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'permissions_count', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')
    inlines = [RolePermissionInline]

    def permissions_count(self, obj):
        count = obj.role_permissions.count()
        return format_html(
            '<a href="?role_id={}">{} permissions</a>',
            obj.id, count
        )
    permissions_count.short_description = 'Permissions'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('role_permissions')

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Clear cache when role is updated
        from django.core.cache import cache
        cache.delete(f'role_permissions_{obj.id}')

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False 

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'permission', 'created_at')
    list_filter = ('role', 'permission__feature_name')
    search_fields = ('role__name', 'permission__permission_code')
    autocomplete_fields = ['role', 'permission']
    readonly_fields = ('id', 'created_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('role', 'permission')

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False 