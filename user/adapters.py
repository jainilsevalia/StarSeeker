from user.tasks import send_allauth_mail
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress
from allauth.utils import valid_email_or_none
from allauth.account.utils import user_field, user_email
from allauth.account.signals import user_signed_up
from django.core.files.temp import NamedTemporaryFile
from django.dispatch import receiver
from django.http.response import HttpResponseRedirect
from django.urls.base import reverse
# from urllib.request import urlopen
import requests
from django.core.files import File

from .models import UserLogin


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return
        if 'email' not in sociallogin.account.extra_data:
            return
        try:
            email = sociallogin.account.extra_data['email'].lower()
            email_address = EmailAddress.objects.get(email__iexact=email)
        except EmailAddress.DoesNotExist:
            return
        user = email_address.user
        sociallogin.connect(request, user)

    def populate_user(self, request, sociallogin, data):
        email = data.get('email')
        # print(data)
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        name = data.get('name')
        user = sociallogin.user
        user_field(user, 'name', name or first_name+' '+last_name)
        user_email(user, valid_email_or_none(email) or '')
        return user


class AccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        login_count = UserLogin.objects.filter(
            generaluser_id=request.user.id).count()
        if(login_count > 1):
            path = "/"
        else:
            path = "/user/onboarding/"
        return path.format(email=request.user.email)

    def save_user(self, request, user, form, commit=True):
        data = form.cleaned_data
        name = data.get('name').title()
        email = data.get('email')
        user_email(user, email)
        user_field(user, 'name', name)
        if 'password1' in data:
            user.set_password(data.get('password1'))
        else:
            user.set_unusable_password()
        if commit:
            user.save()
        return user

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        # TODO: Edit this method to customise the email content.(html template)
        super().send_confirmation_mail(request, emailconfirmation, signup)

    def respond_email_verification_sent(self, request, user):
        return HttpResponseRedirect(reverse('account_signup'))

    def send_mail(self, template_prefix, email, context):
        msg = self.render_mail(template_prefix, email, context)
        send_allauth_mail.delay(msg)


@receiver(user_signed_up)
def populate_user_profile(request, user, sociallogin=None, **kwargs):
    if sociallogin is None:
        return
    if sociallogin.account.provider == 'facebook':
        user_data = user.socialaccount_set.filter(
            provider='facebook')[0].extra_data
        picture_url = "http://graph.facebook.com/" + \
            sociallogin.account.uid + "/picture?type=large"
    if sociallogin.account.provider == 'google':
        user_data = user.socialaccount_set.filter(
            provider='google')[0].extra_data
        picture_url = user_data['picture']
        picture_url = picture_url.rsplit('=s')[0]+'=s300-c'
    img_temp = NamedTemporaryFile()
    response = requests.get(picture_url)
    img_temp.write(response.content)
    img_temp.flush()
    content_type = response.headers['content-type']
    img_extension = '.'+content_type.split('/')[-1]
    img_name = user.userlink+img_extension
    user.profile_picture.save(img_name, File(img_temp))
    user.save()
