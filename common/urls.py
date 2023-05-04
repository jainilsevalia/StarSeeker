from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("tp/<str:userlink>/", views.talentprofile, name="talentprofile"),
    path("search/", views.search, name="search"),
    path("filter/", views.filter, name="filter"),
    path("survey/", views.survey, name="survey"),
    # Footer Links
    path("blogs/", views.blogs, name="blogs"),
    path("contactus/", views.contactus, name="contactus"),
    path("reportbug/", views.reportbug, name="reportbug"),
    path("about/", views.about, name="about"),
    path("support/", views.support, name="support"),
    path("termsofservice/", views.termsofservice, name="termsofservice"),
    path("privacypolicy/", views.privacypolicy, name="privacypolicy"),
    path("bookvenue/", views.bookvenue, name="bookvenue"),
    path("advertisement/", views.advertisement, name="advertisement"),
    path("brandcollaboration/", views.brandcollaboration, name="brandcollaboration"),
    path("sendemailtotalentuser/", views.sendemailtotalentuser, name="sendemailtotalentuser"),
]
