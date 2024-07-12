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
        if len(value) < 7 or not any(char.isdigit() for char in value) or not any(char.isalpha() for char in value):
            raise serializers.ValidationError({
                "status": False,
                "message": "Password must be longer than 8 characters and contain both letters and numbers."
            })
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError({
                "status": False,
                "message": "Email already exists."
            })
        return value

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.pop('confirm_password', None)
        if password != confirm_password:
            raise serializers.ValidationError({
                "status": False,
                "message": "Those passwords don't match."
            })
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'phone', 'email', 'full_name', 'user_type')


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    otp = serializers.CharField()
    email = serializers.EmailField()


class ChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(min_length=8)
    otp = serializers.CharField()

    def validate_email(self, value):
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError({
                "status": False,
                "message": "Email not found in the database"
            })
        return value


class PanerPictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PanerPicture
        fields = ['id', 'picture']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon']


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'picture', 'lat', 'lot']


class RestaurantSerializerAll(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'lat', 'lot', 'picture', 'desc']


class FoodSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializerAll(read_only=True)

    class Meta:
        model = Food
        fields = ['id', 'name', 'picture', 'price', 'restaurant', 'category']


class FoodSerializerAll(serializers.ModelSerializer):
    restaurant = RestaurantSerializerAll(read_only=True)

    class Meta:
        model = Food
        fields = ['id', 'name', 'picture', 'price', 'restaurant', 'category', 'desc']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer', 'restaurant', 'lat', 'lot', 'total_price', 'status', 'date_time', 'items']

    def create(self, validated_data):
        return Order.objects.create(**validated_data)


class FoodCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ['name', 'picture', 'price', 'category', 'desc']

    def create(self, validated_data):
        restaurant = self.context['request'].user.restaurant
        return Food.objects.create(restaurant=restaurant, **validated_data)


class FCMTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMToken
        fields = ['user', 'token']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'timestamp']
