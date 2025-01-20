from rest_framework import serializers
from .models import CustomUser
import re
from datetime import date
from django.contrib.auth import get_user_model, authenticate
from rest_framework.exceptions import AuthenticationFailed

class UserSignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = [
            'full_name', 'username', 'email', 'phone_number', 
            'date_of_birth', 'password', 'confirm_password'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_full_name(self, value):
        """Ensure the full name contains only letters and spaces."""
        if not re.match(r'^[a-zA-Z\s]+$', value):
            raise serializers.ValidationError("Full name must contain only letters and spaces.")
        if len(value) < 3:
            raise serializers.ValidationError("Full name must be at least 3 characters long.")
        return value

    def validate_username(self, value):
        """Ensure the username is alphanumeric and unique."""
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("Username can only contain letters, numbers, and underscores.")
        if len(value) < 5:
            raise serializers.ValidationError("Username must be at least 5 characters long.")
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value

    def validate_email(self, value):
        """Ensure the email is unique and properly formatted."""
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def validate_phone_number(self, value):
        """Ensure the phone number is 10 digits."""
        if not re.match(r'^\d{10}$', value):
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        if CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number is already registered.")
        if value in ['0000000000', '1234567890']:  # Block common fake numbers
            raise serializers.ValidationError("Invalid phone number.")
        return value

    def validate_date_of_birth(self, value):
        """Ensure the user is at least 18 years old."""
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise serializers.ValidationError("You must be at least 18 years old to register.")
        return value

    def validate_password(self, value):
        """Ensure the password is strong."""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value

    def validate(self, data):
        """Ensure password and confirm_password match."""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # Remove confirm_password before saving
        password = validated_data.pop('password')
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
    

User = get_user_model()

class UserLoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get('identifier')
        password = data.get('password')

        try:
            if '@' in identifier:
                user = User.objects.get(email=identifier)
            elif identifier.isdigit():
                user = User.objects.get(phone_number=identifier)
            else:
                user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid login credentials')

        user = authenticate(username=user.username, password=password)
        if not user:
            raise AuthenticationFailed('Invalid login credentials')
        if not user.is_active:
            raise AuthenticationFailed('User account is disabled')

        return user
