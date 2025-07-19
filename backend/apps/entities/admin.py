from django.contrib import admin
from django.utils.html import format_html
from .models import Entity, Platform, Domain, EntityFocalPoint

@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_focal_points_count', 'get_platforms_count', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description', 'focal_points__full_name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    def get_focal_points_count(self, obj):
        return obj.focal_points.count()
    get_focal_points_count.short_description = "Focal Point"

    def get_platforms_count(self, obj):
        return obj.platforms.count()
    get_platforms_count.short_description = "Plateforms"

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False  

class EntityFocalPointInline(admin.TabularInline):
    model = EntityFocalPoint
    extra = 1
    autocomplete_fields = ['focal_point']

@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ( 'get_entity_link', 'get_url_link', 'is_active', 'get_domain_status', 'created_at')
    list_filter = ('is_active', 'entity', 'domain__ssl_issue', 'domain__domain_issue', 'created_at')
    search_fields = ('url', 'entity__name')
    readonly_fields = ('id', 'created_at', 'updated_at', 'domain')
    actions = ['activate_platforms', 'deactivate_platforms']

    def get_entity_link(self, obj):
        url = f"/admin/entities/entity/{obj.entity.id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.entity.name)
    get_entity_link.short_description = "Entité"

    def get_url_link(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>', obj.url, obj.url)
    get_url_link.short_description = "URL"

    def get_domain_status(self, obj):
        if obj.domain.ssl_issue and obj.domain.domain_issue:
            return format_html('<span style="color: red;">SSL & Domain Issues</span>')
        elif obj.domain.ssl_issue:
            return format_html('<span style="color: orange;">SSL Issue</span>')
        elif obj.domain.domain_issue:
            return format_html('<span style="color: orange;">Domain Issue</span>')
        return format_html('<span style="color: green;">OK</span>')
    get_domain_status.short_description = "Statut"

    def activate_platforms(self, request, queryset):
        queryset.update(is_active=True)
    activate_platforms.short_description = "Enable selected platforms"

    def deactivate_platforms(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_platforms.short_description = "Disable selected platforms"

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False  

@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip_address', 'last_scan_date', 'last_ssl_scan_date', 'get_status', 'get_platforms_count')
    list_filter = ('ssl_issue', 'domain_issue', 'last_scan_date', 'last_ssl_scan_date')
    search_fields = ('name', 'ip_address')
    readonly_fields = ('id', 'created_at', 'updated_at')

    def get_status(self, obj):
        if obj.ssl_issue and obj.domain_issue:
            return format_html('<span style="color: red;">SSL & Domain Issues</span>')
        elif obj.ssl_issue:
            return format_html('<span style="color: orange;">SSL Issue</span>')
        elif obj.domain_issue:
            return format_html('<span style="color: orange;">Domain Issue</span>')
        return format_html('<span style="color: green;">OK</span>')
    get_status.short_description = "Statut"

    def get_platforms_count(self, obj):
        return obj.platforms.count()
    get_platforms_count.short_description = "Plateforms"

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False  