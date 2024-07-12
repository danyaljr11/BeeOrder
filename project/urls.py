from django.contrib import admin
from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from api.views import *
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@local.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('banner-pictures/', PanerPictureListView.as_view(), name='banner_pictures'),
    path('create-restaurant/',CreateRestaurantView.as_view(), name='create_restaurant'),
    path('restaurants/', RestaurantListView.as_view(), name='restaurants'),
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('foods/category/<int:category_id>/', FoodByCategoryView.as_view(), name='foods_by_category'),
    path('foods/restaurant/<int:restaurant_id>/', FoodByRestaurantView.as_view(), name='foods_by_restaurant'),
    path('search/', SearchView.as_view(), name='search'),
    path('food/<int:pk>/', FoodDetailView.as_view(), name='food_detail'),
    path('restaurant/<int:pk>/', RestaurantDetailView.as_view(), name='restaurant_detail'),
    path('orders/', PlaceOrderView.as_view(), name='place-order'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/history/', OrderHistoryView.as_view(), name='order-history'),
    path('orders/pending/', PendingOrdersListView.as_view(), name='order-pending'),
    path('orders/<int:order_id>/update-status/', UpdateOrderStatusView.as_view(), name='update-order-status'),
    path('orders/<int:order_id>/cancel/', CancelOrderView.as_view(), name='cancel-order'),
    path('notifications/', ListNotificationsView.as_view(), name='list-notifications'),
    path('getprofile/', GetProfileView.as_view(), name='getprofile'),
    path('add-food/', AddFoodView.as_view(), name='add_food'),
    path('register-fcm-token/', register_fcm_token, name='register-fcm-token'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('manager-login/', RestaurantManagerLoginView.as_view(), name='manager-login'),

]



