from django.contrib import admin
from django.urls import path
from api.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),
    path('verify-otp/', VerifyOTPView.as_view()),
    path('set-new-password', SetNewPasswordView.as_view())


    # Add URLs for Restaurant Manager and Delivery Guy registration and login
]




