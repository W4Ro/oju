from rest_framework import serializers
from .models import SystemLog


class SystemLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = SystemLog
        fields = ['id', 'username', 'details', 'created_at']
        read_only_fields = fields