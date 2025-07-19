from rest_framework import serializers
from .models import Defacement

class DefacementListSerializer(serializers.ModelSerializer):
    entity_name = serializers.CharField(source='entity.name', read_only=True)
    platform_url = serializers.CharField(source='platform.url', read_only=True)
    
    class Meta:
        model = Defacement
        fields = ['id', 'date', 'entity_name', 'platform_url', 'is_defaced']
        read_only_fields = fields

class DefacementDetailSerializer(serializers.ModelSerializer):
    entity_name = serializers.CharField(source='entity.name', read_only=True)
    platform_url = serializers.CharField(source='platform.url', read_only=True)
    
    class Meta:
        model = Defacement
        fields = [
            'id', 'date', 'entity_name', 'platform_url', 'is_defaced',
            'last_state_tree', 'normal_state_tree', 'details'
        ]
        read_only_fields = fields