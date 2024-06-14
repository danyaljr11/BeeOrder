from django.contrib import admin
from django.urls import path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from api.views import *

schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version='v1',
        description="API description",
    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('banner-pictures/', PanerPictureListView.as_view(), name='banner_pictures'),
    path('restaurants/', RestaurantListView.as_view(), name='restaurants'),
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('foods/category/<int:category_id>/', FoodByCategoryView.as_view(), name='foods_by_category'),
    path('foods/restaurant/<int:restaurant_id>/', FoodByRestaurantView.as_view(), name='foods_by_restaurant'),
    path('search/', SearchView.as_view(), name='search'),
    path('food/<int:pk>/', FoodDetailView.as_view(), name='food_detail'),
    path('restaurant/<int:pk>/', RestaurantDetailView.as_view(), name='restaurant_detail'),
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/pending/', PendingOrdersListView.as_view(), name='pending-orders'),
    path('orders/assign/<int:order_id>/', AssignOrderView.as_view(), name='assign-order'),
    path('orders/manager/', OrderListForManagerView.as_view(), name='manager-orders'),
    path('orders/update-status/<int:order_id>/', UpdateOrderStatusView.as_view(), name='update-order-status'),
    path('devices/', FCMDeviceListView.as_view(), name='device-list'),  # List and create FCM devices
    path('devices/<int:pk>/', FCMDeviceDetailView.as_view(), name='device-detail'),  # Retrieve, update and delete FCM device
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
