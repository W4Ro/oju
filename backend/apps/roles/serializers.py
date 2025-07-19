from rest_framework import serializers
from .models import Role, Permission, RolePermission

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'feature_name', 'permission_name', 'permission_code', 'description']
        read_only_fields = ['id']

class RolePermissionSerializer(serializers.ModelSerializer):
    permission_details = PermissionSerializer(source='permission', read_only=True)
    permission_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = RolePermission
        fields = ['id', 'permission_id', 'permission_details']
        read_only_fields = ['id']

class RoleSerializer(serializers.ModelSerializer):
    # permissions = RolePermissionSerializer(source='role_permissions', many=True, read_only=True)
    permission_ids = serializers.SerializerMethodField(read_only=True)
    permissions_to_update = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Role
        # fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at', 
        #          'permissions', 'permission_ids', 'permissions_to_update']
        fields = ['id', 'name', 'description', 'is_active', 'created_at', 'updated_at', 
                 'permission_ids', 'permissions_to_update']
        read_only_fields = ['id', 'created_at']
    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Role name cannot be empty")
        if not (2 <= len(value) <= 255):
            raise serializers.ValidationError("Role name must be between 2 and 255 characters")
        return value

    def validate_description(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Role description cannot be empty")
        if len(value) > 500:
            raise serializers.ValidationError("Role description must not exceed 500 characters")
        return value

    def get_permission_ids(self, obj):
        """Returns the list of permission IDs"""
        return [str(rp.permission.id) for rp in obj.role_permissions.all()]

    def create(self, validated_data):
        permissions = validated_data.pop('permissions_to_update', [])
        role = Role.objects.create(**validated_data)
        
       
        if permissions:
            permissions_objects = Permission.objects.filter(id__in=permissions)
            role_permissions = [
                RolePermission(role=role, permission=permission)
                for permission in permissions_objects
            ]
            RolePermission.objects.bulk_create(role_permissions)
        
        return role

    def update(self, instance, validated_data):
        permissions = validated_data.pop('permissions_to_update', None)
        

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()


        if permissions is not None:

            instance.role_permissions.all().delete()
            
            permissions_objects = Permission.objects.filter(id__in=permissions)
            role_permissions = [
                RolePermission(role=instance, permission=permission)
                for permission in permissions_objects
            ]
            RolePermission.objects.bulk_create(role_permissions)

        return instance

class RoleDetailSerializer(RoleSerializer):
    """Extended serializer for detailed role information"""
    total_permissions = serializers.IntegerField(read_only=True)
    # features_access = serializers.SerializerMethodField()

    class Meta(RoleSerializer.Meta):
        fields = RoleSerializer.Meta.fields + ['total_permissions']# , 'features_access']

    # def get_features_access(self, obj):
    #     """Group permissions by feature"""
    #     features = {}
    #     for role_perm in obj.role_permissions.all():
    #         feature = role_perm.permission.feature_name
    #         if feature not in features:
    #             features[feature] = []
    #         features[feature].append({
    #             'name': role_perm.permission.permission_name,
    #             'code': role_perm.permission.permission_code
    #         })
    #     return features