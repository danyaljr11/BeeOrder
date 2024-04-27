from django.contrib import admin
from django.urls import path
from api.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('customer/register/', CustomerRegisterView.as_view(), name='customer_register'),
    path('customer/login/', CustomerLoginView.as_view(), name='customer_login'),
    path('customer/reset-password/',ResetPasswordView.as_view(), name='reset-password'),
    path('customer/verify-otp/',OTPVerificationView.as_view(), name='verify-otp'),

    # Add URLs for Restaurant Manager and Delivery Guy registration and login
]




