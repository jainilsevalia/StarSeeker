from django.core.mail import EmailMessage, mail_admins
from user.models import GeneralUser
from user.tasks import send_email_from_celery


# Now that the email sending is to be handled by celery, after successfully running the app with celery remove this Util class.
class Util:
    @staticmethod
    def send_mail(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=data['to_email'])
        email.send()

    @staticmethod
    def send_mail_admin(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=data['to_email'])
        email.send()


def send_mail_to_customer(cart):
    mail_subject = "Accepted Booking Request"
    mail_body = "Hello " + cart.generaluser.name + \
        ', \nWe have received your following booking request:'
    for cartitem in cart.cartitem_set.all():
        mail_body += '\n\n' + cartitem.talentuser.generaluser.name + ' for ' + \
            str(cartitem.number_of_days)+' days from '+str(cartitem.start_date)
    mail_body += '\n\nWe will contanct you as soon as possible regarding this. You can see your booking request details under profile section.\nThank you,\nAbhay Bhadani from DuniyaDekhegi.'
    email_data = {'email_subject': mail_subject,
                  'email_body': mail_body, 'to_email': [cart.generaluser.email]}
    send_email_from_celery.delay(email_data)


def send_mails_to_talents(cart):
    email_subject = "New Booking Request"
    for cartitem in cart.cartitem_set.all():
        email_body = 'Hello ' + cartitem.talentuser.generaluser.name+',\nWe have received a booking request for you.\n\nBooking Details:\n\nStart Date :' + \
            str(cartitem.start_date)+'\nNo. of Days : '+str(cartitem.number_of_days)+'\nEvent Type : '+cartitem.event_type + \
            '\nSlot of day : ' + \
            ', '.join(cartitem.slot_of_day) + \
            '\n\nPlease cofirm your request with us.'
        email_data = {'email_subject': email_subject, 'email_body': email_body,
                      'to_email': [cartitem.talentuser.generaluser.email]}
        send_email_from_celery.delay(email_data)


def send_order_completion_mails(cart):
    send_mail_to_customer(cart)
    send_mails_to_talents(cart)

    admins = list(GeneralUser.objects.filter(
        is_superuser=True).values_list('email', flat=True))
    admin_email_subject = "New Booking request made "
    admin_email_body = '\nBooking request by : ' + cart.generaluser.name + " \nHere are other details of the " + \
        cart.generaluser.name + ": \nEmail : " + cart.generaluser.email + \
        "\nMobile Number : " + cart.generaluser.phone_number
    for cartitem in cart.cartitem_set.all():
        admin_email_body += '\n\nBooking request for :' + cartitem.talentuser.generaluser.name + '\nStart Date :'+str(cartitem.start_date)+'\nNo. of Days : '+str(
            cartitem.number_of_days)+'\nEvent Type : '+cartitem.event_type+'\nSlot of day : ' + ', '.join(cartitem.slot_of_day) + '\nAddress : ' + cart.address + '\nCity : ' + cart.city + '\nState : ' + cart.state + '\nPincode : ' + str(cart.pincode)
    admin_email_body += '\n\nTotal Amount : ' + str(cart.total_amount)
    admin_data = {'email_subject': admin_email_subject,
                  'email_body': admin_email_body, 'to_email': admins}
    send_email_from_celery.delay(admin_data)

def talentprofile_created_mail_for_user(talentuser):
    #User
    email_subject = "Talent Profile Created Successfully"
    email_body = 'Hello ' + talentuser.generaluser.name +',\nYour Talent Profile Created Successfully.Thanks for registering on Duniya Dekhegi.'+',\nWe have received a KYC request for you.' + \
        '\n\nWe will contanct you as soon as possible regarding this. You can see your KYC request details under profile section.\nThank you,\nAbhay Bhadani from DuniyaDekhegi.'
    email_data = {'email_subject': email_subject, 'email_body': email_body,
                    'to_email': [talentuser.generaluser.email]}
    send_email_from_celery.delay(email_data)

def talentprofile_created_mail_for_admin(talentuser):
    talentprofile_created_mail_for_user(talentuser)
    #admin
    admins = list(GeneralUser.objects.filter(is_superuser=True).values_list('email', flat=True))
    admin_email_subject = "New KYC request made by " + talentuser.generaluser.name
    admin_email_body = '\nKYC request by : ' + talentuser.generaluser.name + " \nHere are other details of the " + \
        talentuser.generaluser.name + ": \nEmail : " + talentuser.generaluser.email + \
        "\nMobile Number : " + talentuser.generaluser.phone_number
    admin_data = {'email_subject': admin_email_subject,'email_body': admin_email_body, 'to_email': admins}
    send_email_from_celery.delay(admin_data)