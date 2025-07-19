from rest_framework import serializers
from .models import Integration, RTIR, Cerebrate, VirusTotal
from .rtir import RTIRClient
from .cerebrate import CerebrateAPI
from urllib.parse import urlparse
from core.common_function import str_exception
from .virustotal import VirusTotalScanner
from asgiref.sync import async_to_sync

class IntegrationSerializer(serializers.ModelSerializer):
    last_updated = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = Integration
        fields = ['name', 'description', 'last_updated', 'is_active']

    def get_last_updated(self, obj):
        if obj.name.lower() == 'rtir':
            rtir = RTIR.objects.first()
            return rtir.updated_at if rtir else None
        elif obj.name.lower() == 'cerebrate':
            cerebrate = Cerebrate.objects.first()
            return cerebrate.updated_at if cerebrate else None
        elif obj.name.lower() == 'virustotal':
            virustotal = VirusTotal.objects.first()
            return virustotal.updated_at if virustotal else None
        return None

    def get_is_active(self, obj):
        if obj.name.lower() == 'rtir':
            rtir = RTIR.objects.first()
            return rtir.is_active if rtir else False
        elif obj.name.lower() == 'cerebrate':
            cerebrate = Cerebrate.objects.first()
            return cerebrate.is_active if cerebrate else False
        elif obj.name.lower() == 'virustotal':
            virustotal = VirusTotal.objects.first()
            return virustotal.is_active if virustotal else False
        return False

class RTIRSerializer(serializers.ModelSerializer):
    class Meta:
        model = RTIR
        fields = ['url', 'username', 'is_active', 'updated_at']
        read_only_fields = ['updated_at']

    def to_representation(self, instance):
        
        data = super().to_representation(instance)
        return data

class RTIRUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RTIR
        fields = ['url', 'username', 'password', 'is_active']

    def validate_url(self, value):
        try:
            result = urlparse(value)
            if result.scheme not in ['http', 'https']:
                raise serializers.ValidationError(
                    'Bad scheme for url, it might be http or https'
                )
            if not result.netloc:
                raise serializers.ValidationError(
                    'Invalid domain in URL'
                )
        except Exception as e:
            raise serializers.ValidationError(
                f"Invalid URL {str_exception(e)}"
            )
        return value.rstrip('/')
    def update(self, instance, validated_data):
        
        url = validated_data.get('url', instance.url)
        username = validated_data.get('username', instance.username)
        password = validated_data.get('password', instance.password)
        test_rtir = RTIRClient(url, username, password)
        
        if not test_rtir.authenticate():
            raise serializers.ValidationError(
                "URL, username or password incorrect"
            )
            
        return super().update(instance, validated_data)

class CerebrateSerializer(serializers.ModelSerializer):
    refresh_frequency_display = serializers.CharField(
        source='get_refresh_frequency_display',
        read_only=True
    )

    class Meta:
        model = Cerebrate
        fields = [
            'url', 'is_active', 'refresh_frequency',
            'refresh_frequency_display', 'updated_at'
        ]
        read_only_fields = ['updated_at']

class CerebrateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cerebrate
        fields = ['url', 'api_key', 'is_active', 'refresh_frequency']

    def to_representation(self, instance):
        """Hide api_key in response"""
        ret = super().to_representation(instance)
        if instance.api_key:
            ret['api_key'] = '*' * 32
        return ret

    def validate_url(self, value):
        try:
            result = urlparse(value)
            if result.scheme not in ['http', 'https']:
                raise serializers.ValidationError(
                    'Bad scheme for url, it might be http or https'
                )
            if not result.netloc:
                raise serializers.ValidationError(
                    'Invalid domain in URL'
                )
        except Exception as e:
            raise serializers.ValidationError(
                f"Invalid URL {str_exception(e)}"
            )
        return value.rstrip('/')

    
    def validate_refresh_frequency(self, value):
        valid_frequencies = dict(Cerebrate.FREQUENCY_CHOICES).keys()
        if value not in valid_frequencies:
            raise serializers.ValidationError(
                "Invalid refresh rate"
            )
        return value
    

    def update(self, instance, validated_data):
        
        url = validated_data.get('url', instance.url)
        api_key = validated_data.get('api_key', instance.api_key)

        test_cerebrate = CerebrateAPI(url, api_key)
        if not test_cerebrate.check_connection():
            raise serializers.ValidationError(
                "Unable to connect with this API key"
            )
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance
    
class VirusTotalSerializer(serializers.ModelSerializer):
    scan_frequency_display = serializers.CharField(
        source='get_scan_frequency_display',
        read_only=True
    )

    class Meta:
        model = VirusTotal
        fields = [
            'is_active', 'scan_frequency',
            'scan_frequency_display', 'updated_at'
        ]
        read_only_fields = ['updated_at']

class VirusTotalUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirusTotal
        fields = ['api_key', 'is_active', 'scan_frequency']

    def to_representation(self, instance):
        """Hide api_key in response"""
        ret = super().to_representation(instance)
        if instance.api_key:
            ret['api_key'] = '*' * 32
        return ret

    
    def validate_scan_frequency(self, value):
        valid_frequencies = dict(VirusTotal.FREQUENCY_CHOICES).keys()
        if value not in valid_frequencies:
            raise serializers.ValidationError(
                "Invalid refresh rate"
            )
        return value
    

    def update(self, instance, validated_data):
        
        api_key = validated_data.get('api_key', instance.api_key)

        test_virustotal = VirusTotalScanner(api_key)
        try:
            async_to_sync(test_virustotal.verify_api_key)()
        except:
            raise serializers.ValidationError(
                "Unable to verify this API key"
            )
       
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance