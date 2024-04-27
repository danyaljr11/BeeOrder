from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView

from .defs import send_otp
from .serializers import *


class CustomerRegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer
    queryset = User.objects.filter(user_type='customer')

    def post(self, request, *args, **kwargs):
        mutable_data = request.data.copy()  # Make a mutable copy of the data
        password = mutable_data.get('password')
        confirm_password = mutable_data.get('confirm_password')
        if password != confirm_password:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
        return super().post(request, *args, **kwargs)


class CustomerLoginView(APIView):

    def post(self, request):
        serializer = CustomerLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request=request, email=email, password=password)
            if user is not None:
                login(request, user)
                return Response({"message": "Logged in successfully."}, status=status.HTTP_200_OK)
        return Response({"error": "Unable to log in with provided credentials."}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                otp = send_otp(email)
                if otp:
                    # Here you can save the OTP in the user object or in the session for verification
                    return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Failed to send OTP."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPVerificationView(APIView):
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']

            # Retrieve the user by email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

            # Check if the OTP matches
            if user.otp == otp:  # Assuming you have a field 'otp' in your User model
                # OTP is valid, you can now proceed with password reset or any other action
                return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)