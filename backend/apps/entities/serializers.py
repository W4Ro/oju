from rest_framework import serializers
from .models import Entity, Platform, Domain, EntityFocalPoint
from apps.focal_points.serializers import FocalPointSerializer
from apps.focal_points.models import FocalPoint
from urllib.parse import urlparse
from core.common_function import str_exception
from django.db.models import Q

class DomainSerializer(serializers.ModelSerializer):
    """Serializer for Domain model."""
    
    class Meta:
        model = Domain
        fields = [
            'id', 'name', 'last_scan_date', 'last_ssl_scan_date',
            'ssl_issue', 'domain_issue', 'ip_address',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class PlatformSerializer(serializers.ModelSerializer):
    """Serializer for Platform model with custom validation."""
    
    entity_name = serializers.CharField(
        source='entity.name',
        read_only=True
    )

    entity = serializers.PrimaryKeyRelatedField(
        queryset=Entity.objects.all(),
        help_text="Entity owning the platform"
    )

    alerts_count = serializers.IntegerField(
        source='alerts.count',
        read_only=True
    )

    class Meta:
        model = Platform
        fields = [
            'id', 'url', 'is_active', 'entity',
            'entity_name', 'alerts_count',
             'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'domain']

    def validate_url(self, value):
        """Custom URL validation."""
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
        instance = getattr(self, 'instance', None)
        if instance and instance.url == value:
            return value
        normalized_value = value.rstrip('/')
        if Platform.objects.filter(
            Q(url__iexact=normalized_value) |
            Q(url__iexact=normalized_value + '/')
        ).exists():
            raise serializers.ValidationError(
                "This URL is already registered."
            )

        return value
    
    def validate_entity(self, value):
        if not Entity.objects.filter(id=value.id).exists():
            raise serializers.ValidationError(
                "Entity does not exist"
            )
        return value
    
    def create(self, validated_data):
        """Create a platform and automatically manage the associated domain."""
        url = validated_data.get('url')
        domain_name = urlparse(url).netloc.split(':')[0]

        domain, created = Domain.objects.get_or_create(
            name=domain_name,
            defaults={
                'last_scan_date': None,
                'last_ssl_scan_date': None
            }
        )
        validated_data['domain'] = domain
        
        platform = super().create(validated_data)
        return platform

    def update(self, instance, validated_data):
        """Update a platform and manage domain change if necessary."""
        if 'url' in validated_data:
            url = validated_data.get('url')
            domain_name = urlparse(url).netloc.split(':')[0]

            
            if domain_name != instance.domain.name:
                
                domain, created = Domain.objects.update_or_create(
                    name=domain_name,
                    defaults={
                        'last_scan_date': None,
                        'last_ssl_scan_date': None,
                    }
                )
                validated_data['domain'] = domain

        return super().update(instance, validated_data)

class EntitySerializer(serializers.ModelSerializer):
    """Serializer for Entity model with relationship management."""
    
    # platforms = PlatformSerializer(many=True, read_only=True)
    focal_points = FocalPointSerializer(many=True, read_only=True)
    focal_points_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    platforms_count = serializers.IntegerField(
        source='platforms.count',
        read_only=True
    )
    
    alerts_count = serializers.SerializerMethodField(read_only=True)
    alerts_resolution_percentage = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Entity
        fields = [
            'id', 'name', 'description', 'created_at',
            'updated_at',  'platforms_count',
            'focal_points', 'focal_points_ids',
            'alerts_count', 'alerts_resolution_percentage',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_alerts_count(self, obj):
        """
        Returns the number of alerts for the entity.
        """
        return obj.alerts.count()
    
    def get_alerts_resolution_percentage(self, obj):
        """
        Returns the percentage of resolved alerts for the entity.
        """
        total_alerts = obj.alerts.count()
        if total_alerts == 0:
            return 100
        
        resolved_alerts = obj.alerts.filter(
            status__in=['resolved', 'false_positive']
        ).count()

        return int((resolved_alerts / total_alerts) * 100)

    def to_representation(self, instance):
        """
        Controls the display of focal points according to user permissions
        """
        data = super().to_representation(instance)
        
        request = self.context.get('request')
        if request and request.user:
            view = self.context.get('view')
            if view:
                user_permissions = view.get_user_permissions(request.user)
                if 'focal_points_view' not in user_permissions:
                    data['points_focaux'] = []
                if 'platforms_view' not in user_permissions:
                    data['platforms'] = []
        
        return data
    
    def validate_focal_points_ids(self, value):
        """
        Validates that all focal points exist in the database.
        If a single focal point does not exist, the entire operation is rejected.
        """
        if value:

            existing_count = FocalPoint.objects.filter(id__in=value, is_active=True).count()
            
            
            if existing_count != len(value):
                raise serializers.ValidationError(
                    "One or more focal points do not exist or are disabled. Operation canceled."
                )
        
        return value
        
    def validate_name(self, value):
        """Custom name validation."""
        if len(value.strip()) < 2 or len(value.strip()) > 255:
            raise serializers.ValidationError(
                "The name must be between 2 and 255 characters long"
            )
        instance = getattr(self, 'instance', None)
        if instance and instance.name == value:
            return value
        if Entity.objects.filter(name=value).exists():
            raise serializers.ValidationError("This Entity exists already")
        return value.strip()

    def create(self, validated_data):
        points_focaux_ids = validated_data.pop('focal_points_ids', [])
        entity = Entity.objects.create(**validated_data)
        
        
        for focal_point_id in points_focaux_ids:
            EntityFocalPoint.objects.create(
                entity=entity,
                focal_point_id=focal_point_id
            )
        return entity

    def update(self, instance, validated_data):
        points_focaux_ids = validated_data.pop('focal_points_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if points_focaux_ids is not None:
            
            EntityFocalPoint.objects.filter(entity=instance).delete()
            
            for focal_point_id in points_focaux_ids:
                EntityFocalPoint.objects.create(
                    entity=instance,
                    focal_point_id=focal_point_id
                )
        return instance


class EntityAlertStatsSerializer(serializers.ModelSerializer):
    """Serializer for entity alert statistics."""
    
    total_alerts = serializers.IntegerField(read_only=True)
    open_alerts = serializers.IntegerField(read_only=True)
    closed_alerts = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Entity
        fields = ['id', 'name', 'total_alerts', 'open_alerts', 'closed_alerts']