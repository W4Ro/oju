from rest_framework import serializers
from .models import FocalFunction, FocalPoint
from django.core.validators import RegexValidator
import re

class FocalFunctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FocalFunction
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        """Validate function name"""
        value = value.strip()
        

        if not value:
            raise serializers.ValidationError("Focal function name cannot be empty")
        if not (2 <= len(value) <= 255):
            raise serializers.ValidationError("Focal function name must be between 2 and 255 characters")

        if not self.instance: 
            if FocalFunction.objects.filter(name__iexact=value).exists():
                raise serializers.ValidationError("This function name already exists")
        elif self.instance.name.lower() != value.lower():  
            if FocalFunction.objects.filter(name__iexact=value).exists():
                raise serializers.ValidationError("This function name already exists")
                
        return value

class FocalPointSerializer(serializers.ModelSerializer):
    function_name = serializers.CharField(source='function.name', read_only=True)
    phone_number = serializers.ListField(
        child=serializers.CharField(max_length=16,
                                    validators=[
                RegexValidator(
                    regex=r'^\+?1?[\d\s]{9,20}$',
                    message="Phone number must be in the format '+999999999'. Spaces are allowed. Up to 15 digits allowed."
                )
            ]
        ),
        required=True
    )
    
    class Meta:
        model = FocalPoint
        fields = [
            'id', 'full_name', 'phone_number', 'email',
            'function', 'function_name', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_function(self, value):
        """Validate that the function exists and is active"""
        if not FocalFunction.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("This function does not exist")
        return value

    def validate_full_name(self, value):
        """Validate full name"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Full name cannot be empty")
        
        if not (2 <= len(value) <= 255):
            raise serializers.ValidationError("Focal point name must be between 2 and 255 characters")
        
        if not self.instance:  
            if FocalPoint.objects.filter(full_name__iexact=value).exists():
                raise serializers.ValidationError("This name already exists")
        elif self.instance.full_name.lower() != value.lower():  
            if FocalPoint.objects.filter(full_name__iexact=value).exists():
                raise serializers.ValidationError("This name already exists")
                
        return value

    def validate_phone_number(self, value):
        """Validate phone number"""
        cleaned_numbers = []
        instance = self.instance

        for number in value:
            number = number.replace(' ', '')
            number = ''.join(c for c in number if c.isdigit() or c == '+')
            if not number.startswith('+'):
                raise serializers.ValidationError(f"Invalid phone number format: {number}")

            query = FocalPoint.objects.filter(phone_number__contains=[number])
            
            if instance:
                query = query.exclude(id=instance.id)
            
            if query.exists():
                raise serializers.ValidationError(f"This phone number ({number}) is already in use")

            cleaned_numbers.append(number)

        return cleaned_numbers

    def validate_email(self, value):
        """Validate email"""
        value = value.lower().strip()
        
        email_regex = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Invalid email format")
        if not self.instance:  
            if FocalPoint.objects.filter(email__iexact=value).exists():
                raise serializers.ValidationError("This email is already in use")
        elif self.instance.email.lower() != value.lower(): 
            if FocalPoint.objects.filter(email__iexact=value).exists():
                raise serializers.ValidationError("This email is already in use")
                
        return value

class FocalPointListSerializer(serializers.ModelSerializer):
    """Serializer for simplified focal points list"""
    function_name = serializers.CharField(source='function.name', read_only=True)
    
    class Meta:
        model = FocalPoint
        fields = ['id', 'full_name', 'function_name', 'function', 'phone_number', 'email', 'is_active',
            'created_at', 'updated_at']