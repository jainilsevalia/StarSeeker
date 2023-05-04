from django.urls import path
from . import views
urlpatterns = [
    path('',views.home,name='paymenthome'),
    path('paymenthandler/',views.paymenthandler,name='handler')    
]
