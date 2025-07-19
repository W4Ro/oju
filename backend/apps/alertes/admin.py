from django.contrib import admin
from django.utils.html import format_html
from .models import Alert

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['alert_type_display', 'entity_link', 'platform_link', 
                   'status_colored', 'date']
    list_filter = ['alert_type', 'status', 'entity', 'platform', 'date']
    search_fields = ['entity__name', 'platform__url', 'details']
    readonly_fields = ['id', 'date', 'entity', 'platform', 'alert_type']
    date_hierarchy = 'date'

    def alert_type_display(self, obj):
        return obj.get_alert_type_display()
    alert_type_display.short_description = "Alerte Type"

    def entity_link(self, obj):
        return format_html('<a href="{}">{}</a>', 
                         f'/admin/entities/entity/{obj.entity.id}/',
                         obj.entity.name)
    entity_link.short_description = 'Entity'

    def platform_link(self, obj):
        return format_html('<a href="{}">{}</a>',
                         f'/admin/entities/platform/{obj.platform.id}/',
                         obj.platform.url)
    platform_link.short_description = 'Plateform'

    def status_colored(self, obj):
        colors = {
            'in_progress': 'orange',
            'resolved': 'green',
            'false_positive': 'red'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_colored.short_description = 'Statut'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False  