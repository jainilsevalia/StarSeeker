
# TODO: Blank=True should be remove in future
# TODO: add datetimefield in all possible model
from django.db import models
from multiselectfield.db.fields import MultiSelectField


class SignInCarousel(models.Model):
    image = models.ImageField(upload_to='media/signinupcarousel', blank=True)
    carousel_order = models.IntegerField(blank=True)
    talent_appreciation_text = models.CharField(max_length=70, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name


class SignUpCarousel(models.Model):
    image = models.ImageField(upload_to='media/signinupcarousel', blank=True)
    carousel_order = models.IntegerField(blank=True)
    talent_appreciation_text = models.CharField(max_length=70, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.name


class Carousel(models.Model):
    title = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=50, blank=True)
    buttontext = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to='media/carousel/img', blank=True)
    link = models.CharField(max_length=250, blank=True)
    # TODO: Add active deactive feautre
    carousel_order = models.IntegerField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    comment_by = models.ForeignKey(
        "user.GeneralUser", on_delete=models.CASCADE)
    comment_for = models.ForeignKey(
        "user.TalentUser", on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.IntegerField()
    timestamp = models.DateTimeField()

    class Meta:
        unique_together = ['comment_by', 'comment_for']


class Survey(models.Model):
    choices = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    )

    name = models.CharField(max_length=50)
    email = models.EmailField(primary_key=True)
    phone_number = models.CharField(max_length=12)
    gender = models.CharField(max_length=20)
    description = models.TextField()
    primary_skill = models.CharField(max_length=50)
    primary_skill_other = models.CharField(max_length=50, blank=True)
    secondary_skills = models.CharField(max_length=50, blank=True)
    engagement = models.CharField(max_length=20)
    is_trained = models.BooleanField()
    availability = MultiSelectField(choices=choices)
    address = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    state = models.ForeignKey(
        "user.State", on_delete=models.SET_NULL, blank=True, null=True)
    city = models.ForeignKey(
        "user.City", on_delete=models.SET_NULL, blank=True, null=True)
    will_travel = models.BooleanField()
    price = models.CharField(max_length=20)
    price_rate = models.CharField(max_length=50)
    provide_training = models.BooleanField()
    instagram_url = models.URLField()
    facebook_url = models.URLField()
    youtube_url = models.URLField()
    twitter_url = models.URLField()

    def __str__(self):
        return self.email
