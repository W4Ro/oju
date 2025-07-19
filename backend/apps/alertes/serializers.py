from .models import Alert
from rest_framework import serializers


class AlertSerializer(serializers.ModelSerializer):
    entity_name = serializers.CharField(source='entity.name', read_only=True)
    platform_url = serializers.CharField(source='platform.url', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Alert
        fields = ['id', 'date', 'entity', 'entity_name', 'platform', 
                 'platform_url', 'alert_type', 'alert_type_display', 
                 'status', 'status_display', 'details', 'updated_at']
        read_only_fields = ['id', 'date', 'entity', 'platform', 'alert_type', 'details', 'updated_at']

    def validate(self, data):
        if set(data.keys()) - {'status'}:
            raise serializers.ValidationError(
                "Only the 'status' field can be edited"
            )
        return data