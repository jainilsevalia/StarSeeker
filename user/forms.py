from allauth.account.utils import _has_verified_for_login, perform_login
from allauth.account.forms import LoginForm, SignupForm
from allauth.utils import email_address_exists, valid_email_or_none

from django import forms
from django.contrib.auth import authenticate
from django.conf import settings
from django.contrib.auth.password_validation import UserAttributeSimilarityValidator, MinimumLengthValidator, CommonPasswordValidator, NumericPasswordValidator, validate_password

from .models import GeneralUser

class MyLoginForm(LoginForm):
    email = forms.EmailField(label='Email address', widget=forms.EmailInput(
        attrs={'class': 'form-control'}))
    password = forms.CharField(
        label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super(MyLoginForm, self).__init__(*args, **kwargs)
        if 'login' in self.fields.keys():
            del self.fields['login']
        if 'remember' in self.fields.keys():
            del self.fields['remember']

    def user_credentials(self):
        credentials = {}
        credentials['email'] = self.cleaned_data.get('email')
        credentials['password'] = self.cleaned_data.get('password')
        return credentials

    def clean(self):
        credentials = self.user_credentials()
        email = credentials['email']
        password = credentials['password']

        if not email:
            self.add_error('email', 'Email is required')
        if not valid_email_or_none(email):
            self.add_error('email', 'Not a valid Email address')
        if not password:
            self.add_error('password', 'Password is required')
        if not GeneralUser.objects.filter(email=email).exists():
            self.add_error(None, 'No user registered with this Email address')
        user = authenticate(email=email, password=password)
        if user is None or not user.is_active:
            self.add_error(
                None, 'The e-mail address and/or password you specified are not correct')
        if user:
            if not _has_verified_for_login(user, email):
                self.add_error(None, 'This account is not verified yet')
        if user:
            self.user = user
        return self.cleaned_data

    def login(self, request, redirect_url=None):
        email = self.user_credentials().get("email")
        ret = perform_login(
            request,
            self.user,
            email_verification=settings.ACCOUNT_EMAIL_VERIFICATION,
            redirect_url=redirect_url,
            email=email,
        )
        return ret


class MySignupForm(SignupForm):
    name = forms.CharField(label='Name', widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    is_agree_terms = forms.BooleanField(
        widget=forms.CheckboxInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['placeholder'] = ''
        self.fields['email'].label = 'Email Address'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = ''
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = ''
        self.fields['password2'].label = 'Confirm Password'
        if 'email2' in self.fields.keys():
            del self.fields['email2']
        if 'username' in self.fields.keys():
            del self.fields['username']

    def clean_email(self):
        email = self.cleaned_data['email']
        return email

    def clean(self):
        name = self.cleaned_data.get('name')
        email = self.cleaned_data.get('email')
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        is_agree_terms = self.cleaned_data.get('is_agree_terms')
        special_characters = "[!@#$%^&*()_+-{}]"
        if not is_agree_terms:
            self.add_error(
                'is_agree_terms', 'Please accept terms and condition to proceed further')
        if not name:
            self.add_error('name', 'Name is required')
        if any(char.isnumeric() or char in special_characters for char in name):
            self.add_error(
                'name', 'Name should not contain numbers or special characters')
        if len(name) > 50:
            self.add_error(
                'name', 'Name too long. It must be less than 50 characters')
        if not email:
            self.add_error('email', 'Email is required')
        if not valid_email_or_none(email):
            self.add_error('email', 'Email address is not valid')
        if len(email) > 70:
            self.add_error('email', 'Email address is too long')
        if email_address_exists(email):
            self.add_error(
                'email', 'A user is already registered with this Email address')
        if not password1:
            self.add_error('password1', 'Password is required')
        if len(password1) < 8:
            self.add_error(
                'password1', 'Password must be of atleast 8 characters')
        if not any(char.isnumeric() for char in password1):
            self.add_error(
                'password1', 'Password must contian atleat one numeric value')
        if not any(char in special_characters for char in password1):
            self.add_error(
                'password1', 'Password must contain atleast one special character')
        validate_password(password=password1, user=GeneralUser(name=name, email=email), password_validators=(UserAttributeSimilarityValidator(
            user_attributes=['name', 'email']), MinimumLengthValidator(min_length=8), CommonPasswordValidator(), NumericPasswordValidator()))
        if not password2:
            self.add_error('password2', 'Please confirm password')
        if password1 != password2:
            self.add_error('password2', 'Passwords do not match')
        return self.cleaned_data
