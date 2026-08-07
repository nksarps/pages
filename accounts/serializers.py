import re

from .models import User
from rest_framework import serializers

class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, max_length=128, write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'dob', 'phone_number', 'role', 'is_active', 'created_at', 'updated_at', 'password']

        read_only_fields = ['id', 'created_at', 'updated_at', 'is_active', 'role']

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not (re.search(r'[a-zA-Z]', value) and re.search(r'\d', value) and re.search(r'[^a-zA-Z0-9]', value)):
            raise serializers.ValidationError("Password must contain at least one letter, number, and symbol.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            dob=validated_data['dob'],
            phone_number=validated_data['phone_number'],
            role=validated_data.get('role', 'member'),
        )

        user.set_password(validated_data['password'])
        user.save()

        return user