from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(min_length=4)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'phone', 'email', 'password', 'confirm_password', 'full_name', 'user_type')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        # Check that the password is longer than 8 characters and contains both letters and numbers
        if len(value) < 7 or not any(char.isdigit() for char in value) or not any(char.isalpha() for char in value):
            raise serializers.ValidationError(
                "Password must be longer than 8 characters and contain both letters and numbers.")
        return value

    def validate_email(self, value):
        # Check that the email does not already exist
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate(self, data):
        # Check that the two password entries match
        password = data.get('password')
        confirm_password = data.pop('confirm_password', None)
        if password != confirm_password:
            raise serializers.ValidationError("Those passwords don't match.")
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    otp = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(min_length=8)
    otp = serializers.CharField()

    def validate_email(self, value):
        # Check if email exists in the database
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email not found in the database")
        return value
