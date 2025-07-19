from rest_framework import serializers
from .models import MailConfig, EmailLog
import re

class MailConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailConfig
        fields = [
            'smtp_server', 'smtp_port', 'use_tls', 'use_ssl',
            'email_host', 'email_password', 'default_sender_name',
            'default_reply_to', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Hide email password"""
        ret = super().to_representation(instance)
        if instance.email_password:
            ret['email_password'] = '*' * 12
        return ret

    def validate_smtp_server(self, value):
        """Validate SMTP server format"""
        
        domain_regex = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'
        ip_regex = r'^(?:\d{1,3}\.){3}\d{1,3}$'  

        if not re.match(domain_regex, value) and not re.match(ip_regex, value):
            raise serializers.ValidationError("Invalid SMTP server format (must be a valid domain or IP address).")
        
        return value

    def validate(self, data):
        """Cross-field validation"""
        if not 1 <= data.get('smtp_port') <= 65535:
            raise serializers.ValidationError("SMTP port must be between 1 and 65535")
        
        if data.get('use_tls') and data.get('use_ssl'):
            raise serializers.ValidationError({
                "use_tls": "Cannot use both TLS and SSL simultaneously"
            })

       
        if 'default_reply_to' not in data or not data['default_reply_to']:
            data['default_reply_to'] = data.get('email_host')
        

        return data
    

class EmailLogSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = EmailLog
        fields = [
            'id', 'subject', 'to_recipients', 'cc_recipients', 'bcc_recipients',
            'status', 'status_display', 'error_message', 'sent_at', 'created_at'
        ]
        read_only_fields = fields