from django.core.mail import send_mail
from celery import shared_task
import environ
env = environ.Env()


@shared_task
def send_email_task(subject,content,user_email):

    send_mail(
                subject,
                content,
                env('EMAIL_HOST_USER'),
                user_email,
                fail_silently=False,
            )
