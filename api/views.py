from django.db.models import Q
from rest_framework import generics, status, mixins
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated , AllowAny
from rest_framework.response import Response
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.conf import settings
from .permissions import IsRestaurantManager
from .serializers import *
from .models import *
import random
from django.contrib.auth import authenticate
from .signals import order_status_updated
from rest_framework.parsers import MultiPartParser, FormParser

User = settings.AUTH_USER_MODEL


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            user_type = request.data.get('user_type')

            # Authenticate user
            user = authenticate(request, email=email, password=password)

            if not user:
                return Response({
                    "status": False,
                    "message": "Invalid email or password",
                    "data": {}
                }, status=status.HTTP_200_OK)

            # Check user type
            if user.user_type != user_type:
                return Response({
                    "status": False,
                    "message": f"User type mismatch. Expected {user_type} but got {user.user_type}",
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


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            return self.list(request, *args, **kwargs)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_200_OK)


class CreateRestaurantView(APIView):
    permission_classes = [IsAuthenticated, IsRestaurantManager]
    parser_classes = (MultiPartParser, FormParser,)

    def post(self, request):
        serializer = RestaurantSerializerAll(data=request.data)
        if serializer.is_valid():
            # Save the restaurant instance with the current user as the manager
            serializer.save(manager=request.user)
            return Response({
                'status': True,
                'message': 'Restaurant created successfully',
                'data': serializer.data  # Include the entered data in the response
            }, status=status.HTTP_200_OK)
        return Response({
            'status': False,
            'message': serializer.errors,
            'data': request.data  # Include the entered data in the response
        }, status=status.HTTP_200_OK)


class RestaurantListView(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializerAll
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            return self.list(request, *args, **kwargs)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_200_OK)


class FoodByCategoryView(mixins.ListModelMixin, generics.GenericAPIView):
    serializer_class = FoodSerializerAll
    permission_classes = [AllowAny]

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
    serializer_class = FoodSerializerAll
    permission_classes = [AllowAny]

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
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        query = request.data.get('query', '')
        if not query:
            return Response({
                "status": False,
                "message": "Query parameter is required"
            }, status=status.HTTP_200_OK)

        # Search in Restaurant model
        restaurant_queryset = Restaurant.objects.filter(
            name__icontains=query
        )
        restaurant_serializer = RestaurantSerializerAll(restaurant_queryset.distinct(), many=True)

        # Search in Food model
        food_queryset = Food.objects.filter(
            name__icontains=query
        ) | Food.objects.filter(
            restaurant__name__icontains=query
        )
        food_serializer = FoodSerializerAll(food_queryset.distinct(), many=True)

        # Combine results
        combined_results = {
            "restaurants": restaurant_serializer.data,
            "foods": food_serializer.data
        }

        return Response({
            "status": True,
            "results": combined_results
        }, status=status.HTTP_200_OK)


class FoodDetailView(generics.RetrieveAPIView):
    queryset = Food.objects.all()
    serializer_class = FoodSerializerAll
    permission_classes = [AllowAny]

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
    serializer_class = RestaurantSerializerAll
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_200_OK)


class PlaceOrderView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "message": "Order placed successfully", "order": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": False, "message": serializer.errors}, status=status.HTTP_200_BAD_OK)


class OrderDetailView(mixins.RetrieveModelMixin, generics.GenericAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            return self.retrieve(request, *args, **kwargs)
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


class OrderHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        orders = Order.objects.filter(customer=user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response({"status": True, "orders": serializer.data}, status=status.HTTP_200_OK)


class UpdateOrderStatusView(APIView):
    def patch(self, request, order_id, *args, **kwargs):
        try:
            order = Order.objects.get(id=order_id)

            # Example logic to update order status
            new_status = request.data.get('status')
            if new_status:
                order.status = new_status
                order.save()

                return Response({"status": True, "message": "Order status updated successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"status": False, "message": "Missing 'status' parameter in request body"}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"status": False, "message": "Order not found"}, status=status.HTTP_200_OK)


class CancelOrderView(APIView):
    def post(self, request, order_id, *args, **kwargs):
        try:
            order = Order.objects.get(id=order_id)

            # Check if the order is pending before canceling
            if order.status != 'pending':
                return Response({"status": False, "message": "Only pending orders can be canceled"}, status=status.HTTP_200_OK)

            # Proceed with cancellation logic here
            # For example, updating order status to cancel
            order.status = 'canceled'
            order.save()

            return Response({"status": True, "message": "Order successfully canceled"}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"status": False, "message": "Order not found"}, status=status.HTTP_200_OK)


class ListNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        notifications = Notification.objects.filter(user=user).order_by('-timestamp')
        serializer = NotificationSerializer(notifications, many=True)
        return Response({"status": True, "notifications": serializer.data}, status=status.HTTP_200_OK)


# class AssignOrderView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, order_id, *args, **kwargs):
#         try:
#             order = Order.objects.get(id=order_id, status='pending')
#             order.delivery_guy = request.user
#             order.status = 'confirmed'
#             order.save()
#             notify_customer(order.customer, "Order is on the way", order, firebase_apps)
#             return Response({"status": True, "message": "Order assigned successfully", "data": OrderSerializer(order).data})
#         except Order.DoesNotExist:
#             return Response({"status": False, "message": "Order not found or already assigned"}, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"status": False, "message": str(e)}, status=status.HTTP_200_OK)


# class OrderListForManagerView(generics.ListAPIView):
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Order.objects.filter(restaurant__manager=self.request.user)

#     def get(self, request, *args, **kwargs):
#         try:
#             return self.list(request, *args, **kwargs)
#         except Exception as e:
#             return Response({
#                 "status": False,
#                 "message": str(e)
#             }, status=status.HTTP_200_OK)



@api_view(['POST'])
def register_fcm_token(request):
    try:
        user = request.user
        token = request.data.get('token')

        if not token:
            return Response({
                "status": False,
                "message": "FCM token is required"
            }, status=status.HTTP_200_OK)

        FCMToken.objects.update_or_create(user=user, defaults={'token': token})
        return Response({'status': True, 'message': 'FCM token registered successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "status": False,
            "message": str(e)
        }, status=status.HTTP_200_OK)


class GetProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)


class AddFoodView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.user_type != 'restaurant_manager':
            return Response({
                "status": "error",
                "message": "Not authorized."
            }, status=status.HTTP_200_OK)

        serializer = FoodCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Food item added successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": "error",
            "message": "Invalid data.",
            "errors": serializer.errors
        }, status=status.HTTP_200_OK)


class RestaurantManagerLoginView(APIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            user_type = 'restaurant_manager'  # Set the user type explicitly

            # Authenticate user
            user = authenticate(request, email=email, password=password)

            if not user:
                return Response({
                    "status": False,
                    "message": "Invalid email or password",
                    "data": {}
                }, status=status.HTTP_200_OK)

            # Check user type
            if user.user_type != user_type:
                return Response({
                    "status": False,
                    "message": f"User type mismatch. Expected {user_type} but got {user.user_type}",
                    "data": {}
                }, status=status.HTTP_200_OK)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            token = str(refresh.access_token)  # Get the access token

            # Get the associated restaurant (assuming one-to-one relationship)
            try:
                restaurant = Restaurant.objects.get(manager=user)
                restaurant_id = restaurant.id
            except Restaurant.DoesNotExist:
                restaurant_id = None  # Set to null initially

            # Serialize user data
            serializer = UserSerializer(user)

            # Customize the response data
            return Response({
                "status": True,
                "message": "User logged in successfully",
                "data": {
                    "user": serializer.data,
                    "token": token,  # Include the token
                    "restaurant_id": restaurant_id
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": False,
                "message": str(e)
            }, status=status.HTTP_200_OK)
