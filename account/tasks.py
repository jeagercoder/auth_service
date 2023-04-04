from celery import shared_task

from service_lib.helper import NotificationHelper


@shared_task
def send_otp_register(data):
    route = f'/internal/api/v1/notification/email'
    helper = NotificationHelper(route=route)
    helper.post_json(json=data)
