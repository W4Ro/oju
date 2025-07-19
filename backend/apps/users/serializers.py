from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
import re
from apps.roles.models import Role, RolePermission
from .models import User


class UserBaseSerializer(serializers.ModelSerializer):
    """Basic serializer for user information"""
    role_name = serializers.CharField(source='role.name', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'nom_prenom', 'role', 'is_active', 'created_at', 'updated_at', 'role_name']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_nom_prenom(self, value):
        """Name validation"""
        if not 5 <= len(value) < 255:
            raise serializers.ValidationError("Name must be at least 5 characters long and less than 255 characters")
        return value.strip()

    def validate_email(self, value):
        """Email validation"""
        value = value.strip()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise serializers.ValidationError("Invalid email format")
            
        instance = getattr(self, 'instance', None)
        if instance:
            if User.objects.filter(email=value).exclude(id=instance.id).exists():
                raise serializers.ValidationError("User with this email already exists")
        else:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("User with this email already exists")
        return value

    def validate_username(self, value):
        """Username validation"""
        value = value.strip()
        if not 3 <= len(value) < 30:
            raise serializers.ValidationError(
                "Username length must be between 3 and 30 characters"
            )
    
        instance = getattr(self, 'instance', None)
        if instance:
            if User.objects.filter(username__iexact=value).exclude(id=instance.id).exists():
                raise serializers.ValidationError("User with this username already exists")
        else:
            if User.objects.filter(username__iexact=value).exists():
                raise serializers.ValidationError("User with this username already exists")
        return value

    def validate_role(self, value):
        """role validation"""
        if not Role.objects.filter(id=value.id, is_active=True).exists():
            raise serializers.ValidationError("This role is not valid or inactive")
        return value
    

class UserRegisterSerializer(UserBaseSerializer):
    """serializer for user registration"""
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + ['password', 'confirm_password']

    def validate(self, data):

        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                "Differents password didn't match"
            )
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?])[A-Za-z\d!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]{8,}$', data["password"]):
            raise serializers.ValidationError(
                "Password must contain at least 8 characters, "
                "including uppercase, lowercase, number and special character"
            )
        validate_password(data['password'])
        
        data['is_active'] = False

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password')
        

        user = User.objects.create_user(
            **validated_data,
            password=password
        )
        return user


class UserCreateSerializer(UserBaseSerializer):
    """serializer for user creation"""
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + ['password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:    
            raise serializers.ValidationError(
                "Differents password didn't match"
            )
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?])[A-Za-z\d!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]{8,}$', data["password"]):
            raise serializers.ValidationError(
                "Password must contain at least 8 characters, "
                "including uppercase, lowercase, number and special character"
            )
        validate_password(data['password'])
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        user = User.objects.create_user(
            **validated_data,
            password=password
        )
        return user

class UserUpdateSerializer(UserBaseSerializer):
    """serializer for user update"""

    current_password = serializers.CharField(write_only=True)

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + ['current_password']

    def validate_current_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError("Incorrect password")
        return value


    def update(self, instance, validated_data):
        validated_data.pop('current_password', None)
        
        return super().update(instance, validated_data)
        
class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """serializer for user profile update"""
    
    
    class Meta:
        model = User
        fields = ['username', 'email', 'nom_prenom']

    def validate_nom_prenom(self, value):
        """Name validation"""
        if not 5 <= len(value) < 255:
            raise serializers.ValidationError("Name must be at least 5 characters long and less than 255 characters")

        return value.strip()

    def validate_username(self, value):
        value = value.strip()

        if not 3 <= len(value) < 30:
            raise serializers.ValidationError(
                "Username length must be between 3 and 30 characters"
            )
        
        if User.objects.filter(username=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("username already taken.")
        return value

    def validate_email(self, value):
        value = value.strip()

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise serializers.ValidationError("Invalid email format")
        
        if User.objects.filter(email=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value


    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
    

class ChangePasswordSerializer(serializers.Serializer):
    """serializer for changing password"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': "Passwords doesn't match."
            })
        
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?])[A-Za-z\d!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]{8,}$', data["new_password"]):
                raise serializers.ValidationError(
                    "Password must contain at least 8 characters, "
                    "including uppercase, lowercase, number and special character"
                )
        validate_password(data['new_password'])
        
        return data



class ResetPasswordSerializer(serializers.Serializer):
    """serializer for resetting password"""
    token = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': "Passwords doesn't match"
            })
        
        validate_password(data['password'])
        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?])[A-Za-z\d!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]{8,}$', data["password"]):
                raise serializers.ValidationError(
                    "Password must contain at least 8 characters, "
                    "including uppercase, lowercase, number and special character"
                )
        return data
    


class UserProfileSerializer(UserBaseSerializer):
    """Serializer for user profile with permissions"""
    permissions = serializers.SerializerMethodField()

    class Meta(UserBaseSerializer.Meta):
        fields = UserBaseSerializer.Meta.fields + ['permissions']
        read_only_fields = fields

    def get_permissions(self, obj):
        """Get list of permissions for the user"""
        try:
            if not Role.objects.filter(id=obj.role_id, is_active=True).exists():
                return []
            return list(RolePermission.objects.filter(
                role_id=obj.role_id
            ).values_list('permission__permission_code', flat=True))
        except Exception:
            return []




class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    class Meta:
        model = User
        fields = ['id', 'nom_prenom', 'username', 'email', 'role', 
                 'is_active', 'created_at', 'updated_at', 'role_name']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_role(self, value):
        if not Role.objects.filter(id=value.id, is_active=True).exists():
            raise serializers.ValidationError("Invalid or inactive role")
        return value
    
    def validate_email(self, value):
        """Email validation"""
        value = value.strip()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise serializers.ValidationError("Invalid email format")
            
        instance = getattr(self, 'instance', None)
        if instance:
            if User.objects.filter(email=value).exclude(id=instance.id).exists():
                raise serializers.ValidationError("User with this email already exists")
        else:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("User with this email already exists")
        return value

    def validate_username(self, value):
        """Username validation"""
        value = value.strip()
        if not 3 <= len(value) < 30:
            raise serializers.ValidationError(
                "Username length must be between 3 and 30 characters"
            )
            
        instance = getattr(self, 'instance', None)
        if instance:
            if User.objects.filter(username__iexact=value).exclude(id=instance.id).exists():
                raise serializers.ValidationError("User with this username already exists")
        else:
            if User.objects.filter(username__iexact=value).exists():
                raise serializers.ValidationError("User with this username already exists")
        return value

    def validate_nom_prenom(self, value):
        """Name validation"""
        if not 5 < len(value) < 255:
            raise serializers.ValidationError("Name must be at least 5 characters long and less than 255 characters")

        return value.strip()
