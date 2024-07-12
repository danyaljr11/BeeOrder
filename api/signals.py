from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, FCMToken
from .firebase import send_fcm_notification


@receiver(post_save, sender=Order)
def order_status_updated(sender, instance, created, **kwargs):
    if created:
        # Notify the restaurant manager when a new order is placed (status 'pending')
        try:
            manager_token = FCMToken.objects.get(user=instance.restaurant.manager).token
            send_fcm_notification(manager_token, 'New Order', 'You have a new order from a customer.')
        except FCMToken.DoesNotExist:
            pass  # Handle the case where the manager does not have an FCM token

    if instance.status == 'accepted':
        try:
            customer_token = FCMToken.objects.get(user=instance.customer).token
            send_fcm_notification(customer_token, 'Order Accepted', 'Your order has been accepted by the restaurant.')
        except FCMToken.DoesNotExist:
            pass  # Handle the case where the customer does not have an FCM token

        delivery_tokens = FCMToken.objects.filter(user__user_type='delivery_guy').values_list('token', flat=True)
        for token in delivery_tokens:
            send_fcm_notification(token, 'Order Available', 'A new order is available for delivery.')

    elif instance.status == 'on_the_way':
        try:
            customer_token = FCMToken.objects.get(user=instance.customer).token
            send_fcm_notification(customer_token, 'Order On The Way', 'A delivery guy is on the way to deliver your order.')
        except FCMToken.DoesNotExist:
            pass  # Handle the case where the customer does not have an FCM token

    elif instance.status == 'delivered':
        try:
            customer_token = FCMToken.objects.get(user=instance.customer).token
            send_fcm_notification(customer_token, 'Order Delivered', 'Your order has been delivered.')
        except FCMToken.DoesNotExist:
            pass  # Handle the case where the customer does not have an FCM token
