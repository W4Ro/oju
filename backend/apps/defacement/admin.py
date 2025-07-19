from django.contrib import admin
from .models import Defacement

@admin.register(Defacement)
class DefacementAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'entity', 'platform', 'is_defaced')
    list_filter = ('is_defaced', 'entity', 'platform', 'date')
    search_fields = ('entity__name', 'platform__url', 'details')
    readonly_fields = (
        'id', 'date', 'entity', 'platform', 'is_defaced',
        'normal_state', 'last_state', 'details',
        'normal_state_tree', 'last_state_tree'
    )
    date_hierarchy = 'date'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False  