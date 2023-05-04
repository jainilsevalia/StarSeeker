from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('myprofile/', views.myprofile, name="myprofile"),
    path('editprofile/', views.editprofile, name="editprofile"),
    path('deleteaccount/<str:userlink>/',
         views.deleteaccount, name="deleteaccount"),
    path('onboarding/', views.onboarding, name="onboarding"),
    path('edittalentprofile/',
         views.edittalentprofile, name="edittalentprofile"),
    path('signout/', views.signout, name="signout"),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="site/password_reset.html"),
         name="password_reset"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="site/password_reset_done.html"),
         name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="site/password_reset_form.html"),
         name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name="site/password_reset_sent.html"), name="password_reset_complete"),
]
