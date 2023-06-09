"""duniyadekhegi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from user.views import MyLoginView, MySignupView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("common.urls")),
    path("", include("booking.urls")),
    path("store/",include("store.urls")),
    path("payment/", include("payment.urls")),
    path("accounts/login/", MyLoginView.as_view(), name="account_login"),
    path("accounts/signup/", MySignupView.as_view(), name="account_signup"),
    path("accounts/", include("allauth.urls")),
    path("user/", include("user.urls")),
    path("", include("pwa.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
