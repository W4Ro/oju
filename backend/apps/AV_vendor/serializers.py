from rest_framework import serializers
from .models import AVVendor

class AVVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = AVVendor
        fields = ['id', 'name', 'contact', 'comments', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        """
        Checks the uniqueness of the name
        """
        
        if not self.instance:
            if AVVendor.objects.filter(name=value).exists():
                raise serializers.ValidationError("An AV vendor with this name already exists")
        
        elif self.instance.name != value:  
            if AVVendor.objects.filter(name=value).exists():
                raise serializers.ValidationError("An AV vendor with this name already exists")

        if not value or len(value) < 3 or len(value) > 255:
            raise serializers.ValidationError(
                "Vendor name must be between 3 and 255 characters long"
            )
        
        return value.strip()
    
    def validate_contact(self, value):
        """
        Validates the contact field
        """
        if not value or len(value) < 3 or len(value) > 255:
            raise serializers.ValidationError(
                "Contact must be between 3 and 255 characters long"
            )
        
        return value.strip()
    
    def validate_comments(self, value):
        """
        Validates the comments field
        """
        if not value or len(value) > 500:
            raise serializers.ValidationError(
                "Comments cannot exceed 500 characters"
            )
        
        return value.strip()