from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
import random
from django.contrib.auth import logout, authenticate


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)

        if not user:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)

        # Serialize user data
        serializer = UserSerializer(user)

        # Customize the response data
        response_data = {
            "user": serializer.data,
            "token": token
        }

        return Response(response_data, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
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


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        # Generate OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(4)])

        # Send OTP via email
        send_mail(
            'Password Reset OTP',
            f'Your OTP is: {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        # Store the email and OTP in the session
        request.session['reset_password_email'] = email
        request.session['reset_password_otp'] = otp

        return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        otp_entered = request.data.get('otp')
        email = request.session.get('reset_password_email')
        stored_otp = request.session.get('reset_password_otp')

        if not email or not stored_otp:
            return Response({"error": "Email or OTP not found in session"}, status=status.HTTP_200_OK)

        if stored_otp != otp_entered:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_200_OK)

        # Clear the OTP from the session after successful verification
        del request.session['reset_password_otp']

        return Response({"message": "OTP verified successfully, please provide your new password"},
                        status=status.HTTP_200_OK)


class SetNewPasswordView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def post(self, request, *args, **kwargs):
        new_password = request.data.get('new_password')
        email = request.session.get('reset_password_email')

        if not email:
            return Response({"error": "Email not found in session"}, status=status.HTTP_200_OK)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_200_OK)

        # Reset password
        user.set_password(new_password)
        user.save()

        # Clear the session after password reset
        del request.session['reset_password_email']

        return Response({"message": "Password reset successfully, please login with your new password"},
                        status=status.HTTP_200_OK)
