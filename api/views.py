from django.db.models import Q
from rest_framework import generics, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.mail import send_mail
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from .notifications import *
from .serializers import *
from .models import *
import random
from django.contrib.auth import logout, authenticate
from .permissions import IsRestaurantManager


User = settings.AUTH_USER_MODEL


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return Response({
                "status": True,
                "message": "User registered successfully",
                "data": response.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_200_OK)


class LoginView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            password = request.data.get('password')

            user = authenticate(request, email=email, password=password)

            if not user:
                return Response({
                    "status": False,
                    "message": "Invalid email or password",
                    "data": {}
                }, status=status.HTTP_200_OK)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)

            # Serialize user data
            serializer = UserSerializer(user)

            # Customize the response data
            return Response({
                "status": True,
                "message": "User logged in successfully",
                "data": {
                    "user": serializer.data,
                    "token": token
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Invalidate the token
            token = request.data.get('token')
            if token:
                try:
                    # Blacklist the token
                    BlacklistedToken.objects.create(token=token)
                except Exception as e:
                    # Handle exception, e.g., token already blacklisted
                    pass

            # Perform logout (clear session)
            logout(request)

            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_200_OK)


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data.get('email')

            # Generate OTP
            otp = ''.join([str(random.randint(0, 9)) for _ in range(4)])

            # Store OTP in the database
            user = CustomUser.objects.get(email=email)
            user.otp = otp
            user.save()

            # Send OTP via email
            send_mail(
                'Password Reset OTP',
                f'Your OTP is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            return Response({"status": True, "message": "OTP sent to your email"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_200_OK)


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        try:
            otp_entered = request.data.get('otp')
            email = request.data.get('email')

            # Check if email exists in the database
            if not CustomUser.objects.filter(email=email).exists():
                return Response({"status": False, "message": "Email not found in the database"}, status=status.HTTP_200_OK)

            # Check if the entered OTP matches the stored OTP
            user = CustomUser.objects.get(email=email)
            stored_otp = user.otp
            if not stored_otp or stored_otp != otp_entered:
                return Response({"status": False, "message": "Invalid OTP"}, status=status.HTTP_200_OK)

            return Response({"status": True, "message": "OTP verified successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_200_OK)


class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data.get('email')
            otp_entered = serializer.validated_data.get('otp')
            new_password = serializer.validated_data.get('new_password')

            # Check if email exists in the database
            if not CustomUser.objects.filter(email=email).exists():
                return Response({"status": False, "message": "Email not found in the database"}, status=status.HTTP_200_OK)

            # Check if the entered OTP matches the stored OTP
            user = CustomUser.objects.get(email=email)
            stored_otp = user.otp
            if not stored_otp or stored_otp != otp_entered:
                return Response({"status": False, "message": "Invalid OTP"}, status=status.HTTP_200_OK)

            # Update user's password
            user.set_password(new_password)
            user.save()

            # Clear the OTP from the database
            user.otp = None
            user.save()

            return Response({"status": True, "message": "Password changed successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_200_OK)


class PanerPictureListView(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = PanerPicture.objects.all()
    serializer_class = PanerPictureSerializer

    def get(self, request, *args, **kwargs):
        try:
            return self.list(request, *args, **kwargs)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_200_OK)


class RestaurantListView(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    def get(self, request, *args, **kwargs):
        try:
            return self.list(request, *args, **kwargs)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_200_OK)


class CategoryListView(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get(self, request, *args, **kwargs):
        try:
            return self.list(request, *args, **kwargs)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_200_OK)


class FoodByCategoryView(mixins.ListModelMixin, generics.GenericAPIView):
    serializer_class = FoodSerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Food.objects.filter(category_id=category_id)

    def get(self, request, *args, **kwargs):
        try:
            return self.list(request, *args, **kwargs)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_200_OK)


class FoodByRestaurantView(mixins.ListModelMixin, generics.GenericAPIView):
    serializer_class = FoodSerializer

    def get_queryset(self):
        restaurant_id = self.kwargs['restaurant_id']
        return Food.objects.filter(restaurant_id=restaurant_id)

    def get(self, request, *args, **kwargs):
        try:
            return self.list(request, *args, **kwargs)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_200_OK)


class SearchView(generics.GenericAPIView):
    serializer_class = serializers.Serializer  # Dummy serializer class

    def post(self, request, *args, **kwargs):
        try:
            query = self.request.data.get('query', '')
            food_results = Food.objects.filter(Q(name__icontains=query))
            restaurant_results = Restaurant.objects.filter(Q(name__icontains=query))

            food_serializer = FoodSerializer(food_results, many=True)
            restaurant_serializer = RestaurantSerializer(restaurant_results, many=True)

            return Response({
                'foods': food_serializer.data,
                'restaurants': restaurant_serializer.data
            })
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_200_OK)


class FoodDetailView(generics.RetrieveAPIView):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_200_OK)


class RestaurantDetailView(generics.RetrieveAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_200_OK)


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(customer=user)

    def create(self, request, *args, **kwargs):
        try:
            request.data['customer'] = request.user.id
            response = super().create(request, *args, **kwargs)

            # Notify the restaurant manager about the new order
            order_data = response.data
            notify_manager(order_data['restaurant'], order_data, firebase_apps)

            return Response({
                "status": True,
                "message": "Order created successfully",
                "data": response.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_200_OK)


class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'customer':
            return Order.objects.filter(customer=user)
        elif user.user_type == 'delivery_guy':
            return Order.objects.filter(delivery_guy=user)
        elif user.user_type == 'restaurant_manager':
            return Order.objects.filter(restaurant__manager=user)

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_200_OK)


class PendingOrdersListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(status='pending')

    def get(self, request, *args, **kwargs):
        try:
            return self.list(request, *args, **kwargs)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)},
                status=status.HTTP_200_OK)


class AssignOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id, *args, **kwargs):
        try:
            order = Order.objects.get(id=order_id, status='pending')
            order.delivery_guy = request.user
            order.status = 'confirmed'
            order.save()
            notify_customer(order.customer, "Order is on the way", order, firebase_apps)
            return Response({"status": True, "message": "Order assigned successfully", "data": OrderSerializer(order).data})
        except Order.DoesNotExist:
            return Response({"status": False, "message": "Order not found or already assigned"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=status.HTTP_200_OK)


class OrderListForManagerView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsRestaurantManager]

    def get_queryset(self):
        return Order.objects.filter(restaurant__manager=self.request.user)

    def get(self, request, *args, **kwargs):
        try:
            return self.list(request, *args, **kwargs)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_200_OK)


class UpdateOrderStatusView(APIView):
    permission_classes = [IsAuthenticated, IsRestaurantManager]

    def post(self, request, order_id, *args, **kwargs):
        try:
            order = Order.objects.get(id=order_id)
            new_status = request.data.get('status')
            if new_status not in dict(Order.STATUS_CHOICES):
                return Response({"status": False, "message": "Invalid status"}, status=status.HTTP_200_OK)
            order.status = new_status
            order.save()
            if new_status == 'confirmed':
                notify_delivery_guys(order, firebase_apps)
            elif new_status == 'rejected':
                notify_customer(order.customer, "Your order was rejected", order, firebase_apps)
            return Response({"status": True, "message": "Order status updated successfully", "data": OrderSerializer(order).data})
        except Order.DoesNotExist:
            return Response({"status": False, "message": "Order not found"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "message": str(e)}, status=status.HTTP_200_OK)


class FCMRegistrationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = FCMDeviceSerializer(data=request.data)
        if serializer.is_valid():
            FCMDevice.objects.update_or_create(user=request.user, defaults={'registration_id': serializer.validated_data['registration_id']})
            return Response({"status": True, "message": "FCM token registered successfully"}, status=status.HTTP_201_CREATED)
        return Response({"status": False, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class FCMDeviceListView(generics.ListCreateAPIView):
    queryset = FCMDevice.objects.all()
    serializer_class = FCMDeviceSerializer
    permission_classes = [IsAuthenticated]


class FCMDeviceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FCMDevice.objects.all()
    serializer_class = FCMDeviceSerializer
    permission_classes = [IsAuthenticated]