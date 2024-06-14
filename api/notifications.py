import firebase_admin
from firebase_admin import credentials
from django.conf import settings
from firebase_admin import messaging
from api.models import FCMDevice, CustomUser

User = settings.AUTH_USER_MODEL


# def initialize_firebase_apps():
#     firebase_apps = {}
#
#     # Initialize Customer Firebase App
#     customer_cred = credentials.Certificate('path/to/serviceAccountKey_customer.json')
#     customer_app = firebase_admin.initialize_app(customer_cred, name='customer_app')
#     firebase_apps['customer'] = customer_app
#
#     # Initialize Restaurant Manager Firebase App
#     manager_cred = credentials.Certificate('path/to/serviceAccountKey_restaurant_manager.json')
#     manager_app = firebase_admin.initialize_app(manager_cred, name='manager_app')
#     firebase_apps['restaurant_manager'] = manager_app
#
#     # Initialize Delivery Guy Firebase App
#     delivery_guy_cred = credentials.Certificate('path/to/serviceAccountKey_delivery_guy.json')
#     delivery_guy_app = firebase_admin.initialize_app(delivery_guy_cred, name='delivery_guy_app')
#     firebase_apps['delivery_guy'] = delivery_guy_app
#
#     return firebase_apps
#
#
# firebase_apps = initialize_firebase_apps()


def notify_manager(restaurant_id, order_data, firebase_apps):
    try:
        # Fetch the restaurant manager associated with the restaurant
        manager = CustomUser.objects.get(restaurant__id=restaurant_id, user_type='restaurant_manager')

        # Fetch the FCM device for the manager
        fcm_device = FCMDevice.objects.get(user=manager)

        # Prepare and send the notification message
        message = messaging.Message(
            data={
                "order_id": str(order_data['id']),
                "status": order_data['status']
            },
            token=fcm_device.registration_id
        )
        messaging.send(message, app=firebase_apps['restaurant_manager'])

    except CustomUser.DoesNotExist:
        pass  # Handle case where manager doesn't exist
    except FCMDevice.DoesNotExist:
        pass  # Handle case where FCM device for manager doesn't exist


def notify_customer(customer, message_text, order, firebase_app):
    try:
        fcm_device = FCMDevice.objects.get(user=customer)
        message = messaging.Message(
            data={
                "order_id": str(order.id),
                "status": order.status
            },
            notification=messaging.Notification(
                title="Order Update",
                body=message_text
            ),
            token=fcm_device.registration_id
        )
        messaging.send(message, app=firebase_app['customer'])
    except FCMDevice.DoesNotExist:
        pass


def notify_delivery_guys(order, firebase_app):
    delivery_guys = User.objects.filter(user_type='delivery_guy')
    for delivery_guy in delivery_guys:
        try:
            fcm_device = FCMDevice.objects.get(user=delivery_guy)
            message = messaging.Message(
                data={
                    "order_id": str(order.id),
                    "status": order.status
                },
                notification=messaging.Notification(
                    title="New Delivery Order",
                    body=f"Order {order.id} needs to be delivered"
                ),
                token=fcm_device.registration_id
            )
            messaging.send(message, app=firebase_app['delivery_guy'])
        except FCMDevice.DoesNotExist:
            pass
