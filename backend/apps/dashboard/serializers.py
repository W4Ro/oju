from rest_framework import serializers
from apps.entities.models import Platform

class StatisticsSerializer(serializers.Serializer):
    """
    Serializer for monthly statistics data.
    Used for both entity and platform count statistics.
    """
    month = serializers.CharField(help_text="Month name (abbreviated)")
    count = serializers.IntegerField(help_text="Count for the specific month")

class PlatformUrlScreenshotSerializer(serializers.ModelSerializer):
    screenshot_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Platform
        fields = ['url', 'screenshot_url']
    
    def get_screenshot_url(self, obj):
        """
        Returns the URL of the screenshot for the platform.
        """
        if not obj.screenshot:
            return None        
        
        return f"/entities/platforms/screenshots/{obj.id}.png/"

class EntityStatisticsSerializer(serializers.Serializer):
    """
    Serializer for entity statistics with monthly breakdown.
    """
    name = serializers.CharField(default="Total Entity", help_text="Name of the statistic")
    data = StatisticsSerializer(many=True, help_text="Monthly data points")

class PlatformStatisticsSerializer(serializers.Serializer):
    """
    Serializer for platform statistics with monthly breakdown.
    """
    name = serializers.CharField(default="Total Platforms", help_text="Name of the statistic")
    data = StatisticsSerializer(many=True, help_text="Monthly data points")

class AlertCategorySerializer(serializers.Serializer):
    """
    Serializer for alert categories statistics.
    """
    labels = serializers.ListField(
        child=serializers.CharField(),
        help_text="Category labels"
    )
    data = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Count for each category"
    )
    colors = serializers.ListField(
        child=serializers.CharField(),
        help_text="Colors for each category"
    )

class EntityAlertSerializer(serializers.Serializer):
    """
    Serializer for entity alert statistics.
    """
    name = serializers.CharField(help_text="Entity name")
    data = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Monthly alert counts"
    )

class MostImpactedEntitiesSerializer(serializers.Serializer):
    """
    Serializer for the most impacted entities with monthly breakdown.
    """
    entities = EntityAlertSerializer(many=True, help_text="Entity alert data")
    categories = serializers.ListField(
        child=serializers.CharField(),
        help_text="Month categories (abbreviated names)"
    )
    colors = serializers.ListField(
        child=serializers.CharField(),
        help_text="Colors for each entity line"
    )

class CaseByCategorySerializer(serializers.Serializer):
    """
    Serializer for cases by category statistics.
    """
    name = serializers.CharField(help_text="Data series name")
    data = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Count for each category"
    )
    categories = serializers.ListField(
        child=serializers.CharField(),
        help_text="Alert type categories"
    )
    colors = serializers.ListField(
        child=serializers.CharField(),
        help_text="Colors for each category"
    )

class AttackDataItemSerializer(serializers.Serializer):
    """
    Serializer for individual attack data items.
    """
    value = serializers.IntegerField(help_text="Number of cases")
    name = serializers.CharField(help_text="Attack category name")

class EntityAttackDataSerializer(serializers.Serializer):
    """
    Serializer for entity-specific attack data.
    """
    entities = serializers.DictField(
        child=serializers.ListField(child=AttackDataItemSerializer()),
        help_text="Map of entity names to their attack data"
    )

class RecentAlertSerializer(serializers.Serializer):
    """
    Serializer for recent alerts list.
    """
    id = serializers.CharField(help_text="Alert ID")
    url = serializers.CharField(help_text="Platform URL")
    entity = serializers.CharField(help_text="Entity Name")
    created_at = serializers.CharField(help_text="Formatted creation date")
    type = serializers.CharField(help_text="Alert Type")

    def to_representation(self, instance):
        return {
            'id': instance['id'],
            'url': instance['url'],
            'entity': instance['entity'],
            'created_at': instance['created_at'],
            'type': instance['type'],
        }