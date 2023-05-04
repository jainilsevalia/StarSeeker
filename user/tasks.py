from celery import shared_task
from django.core.mail import EmailMessage
from templated_email import get_templated_mail

@shared_task
def send_email_from_celery(data):
    msg = EmailMessage(subject='[DuniyaDekhegi] '+data['email_subject'],body=data['email_body'],to=data['to_email'])
    msg.send()
    return None
    
@shared_task
def send_allauth_mail(msg):
    msg.send()
    return None

@shared_task
def send_templated_email_celery(data):
    msg = get_templated_mail( 
        template_name= data["template_name"],
        from_email= data["from_email"],
        to= data["recipient_list"],
        context= data["context"],
    )
    msg.send()
    return None