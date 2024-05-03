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
    path('change-password/', ChangePasswordView.as_view()),
    path('paner_pictures/', PanerPictureListView.as_view()),
    path('restaurants/', RestaurantListView.as_view()),
    path('categories/', CategoryListView.as_view()),
    path('foods/category/<int:category_id>/', FoodByCategoryView.as_view()),
    path('foods/restaurant/<int:restaurant_id>/', FoodByRestaurantView.as_view()),
    path('search/', SearchView.as_view()),
    path('foods/<int:pk>', FoodDetailView.as_view()),
    path('restaurants/<int:pk>', RestaurantDetailView.as_view()),

]




