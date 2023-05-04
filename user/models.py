from django.contrib.auth.signals import user_logged_in
from django.db import models
from django.db.models import F
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.dispatch import receiver
from django.utils import timezone
from common.models import Comment

from duniyadekhegi.utils import unique_slug_generator
from multiselectfield import MultiSelectField
from ckeditor.fields import RichTextField
from booking.models import Cart
from store.models import Product, StoreOrder


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError("Email is required")
        if not name:
            raise ValueError("Name is required")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(
            email=self.normalize_email(email),
            name=name,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True

        user.save(using=self._db)
        return user


class GeneralUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=70, unique=True)
    name = models.CharField(max_length=50)
    userlink = models.SlugField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(verbose_name="phone number", max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to="media/generalprofile/img", null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    date_created = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["name"]
    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    @property
    def wishlist_talentusers(self):
        wishlist = self.wishlist.wishlistitem_set.all()
        talentuser_list = []
        for item in wishlist:
            talentuser = item.talentuser
            talentuser_list.append(talentuser)
        return talentuser_list
    @property
    def wishlist_products(self):
        w_ids = ProductWishlist.objects.filter(wishlist_of=self).values_list('wishlist_product')
        wishlist_products = Product.objects.filter(id__in=w_ids)
        return wishlist_products
    @property
    def user_cart(self):
        cart, _ = Cart.objects.get_or_create(generaluser=self, is_complete=False)
        return cart

    @property
    def store_cart(self):
        cart, _ = StoreOrder.objects.get_or_create(user=self, is_complete=False)
        return cart

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.userlink:
            self.userlink = unique_slug_generator(self)
        super(GeneralUser, self).save(*args, **kwargs)

    @property
    def progress(self):
        profile_progress = 0
        if self.name:
            profile_progress += 33
        if self.phone_number:
            profile_progress += 33
        if self.profile_picture:
            profile_progress += 33
        return profile_progress

    @property
    def address(self):
        try:
            address = Address.objects.get(generaluser=self, is_default=True)
        except:
            address = {}
        return address

    @property
    def otherCountry(self):
        try:
            address = OtherCountry.objects.get(generaluser=self, is_default=True)
        except:
            address = {}
        return address

    @property
    def login_count(self):
        count = UserLogin.objects.filter(generaluser=self).count()
        return count

class UserLogin(models.Model):
    generaluser = models.ForeignKey(GeneralUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()


def update_user_login(sender, user, **kwargs):
    user.userlogin_set.create(timestamp=timezone.now())
    user.save()
    cart, _ = Cart.objects.get_or_create(generaluser=user, is_complete=False)


user_logged_in.connect(update_user_login)


class OtherCountry(models.Model):
    generaluser = models.ForeignKey(GeneralUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=150, blank=True)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    pincode = models.CharField(max_length=15, blank=True)
    is_default = models.BooleanField(default=False)


class State(models.Model):
    name = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.name


class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.name


class Address(models.Model):
    generaluser = models.ForeignKey(GeneralUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=150, blank=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True)
    pincode = models.CharField(max_length=15, blank=True)
    is_default = models.BooleanField(default=False)


class TalentUser(models.Model):
    generaluser = models.OneToOneField(GeneralUser, on_delete=models.CASCADE, related_name="talentuser")
    availability_choices = (
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    )
    is_kyc_done = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    description = RichTextField(blank=True)
    achievements = models.TextField(blank=True)
    thumbnail = models.FileField(upload_to="media/talentprofile/img/thumbnail", blank=True)
    # MORE INFO
    gender = models.CharField(max_length=20)
    secondary_skills = models.CharField(max_length=50, blank=True)
    engagement = models.CharField(max_length=20)
    is_trained = models.BooleanField()
    availability = MultiSelectField(choices=availability_choices)
    will_travel = models.BooleanField()
    provide_training = models.BooleanField()

    def __str__(self):
        return self.generaluser.email

    @property
    def rating_avg(self):
        average = Comment.objects.filter(comment_for=self).aggregate(models.Avg("rating"))["rating__avg"]
        if average:
            return average
        return 0

    @property
    def email(self):
        return "%s" % (self.generaluser.email)

    @property
    def name(self):
        return "%s" % (self.generaluser.name)

    @property
    def last_login(self):
        return "%s" % (self.generaluser.last_login)

    @property
    def date_created(self):
        return "%s" % (self.generaluser.date_created)

    @property
    def category(self):
        try:
            category = Category.objects.get(talentuser=self)
        except:
            category = None
        return category
class Seller(models.Model):
    generaluser = models.OneToOneField(GeneralUser, on_delete=models.CASCADE, related_name="seller")
    store_name = models.CharField(max_length=50, blank=True)
    store_description = models.TextField(blank=True)
    store_logo = models.ImageField(upload_to="media/store/logo/", blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_kyc_done = models.BooleanField(default=False)

    def __str__(self):
        return self.generaluser.email

class Category(models.Model):
    talentuser = models.ForeignKey(TalentUser, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class TalentImage(models.Model):
    talentuser = models.ForeignKey(TalentUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="media/talentprofile/img/content", null=True, blank=True)
    image_order = models.IntegerField(blank=True, default=0)
    upload_date = models.DateTimeField(auto_now_add=True)

    def delete(self, using=None, keep_parents=False):
        self.image.storage.delete(self.image.name)
        super().delete()


class TalentVideo(models.Model):
    talentuser = models.ForeignKey(TalentUser, on_delete=models.CASCADE)
    video = models.FileField(upload_to="media/talentprofile/video", blank=True)
    video_order = models.IntegerField(blank=True, default=0)
    upload_date = models.DateTimeField(auto_now_add=True)


class EmbeddedVideo(models.Model):
    talentuser = models.ForeignKey(TalentUser, on_delete=models.CASCADE)
    embed_video_url = models.CharField(max_length=500, blank=True)
    # embeded_video_order = models.IntegerField(blank=True, default=0)
    upload_date = models.DateTimeField(auto_now_add=True)


class FAQ(models.Model):
    talentuser = models.ForeignKey(TalentUser, on_delete=models.CASCADE)
    question = models.CharField(max_length=250, blank=True)
    answer = models.CharField(max_length=250, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question


class Wishlist(models.Model):
    wishlist_of = models.ForeignKey(GeneralUser, on_delete=models.CASCADE)
    wishlist_profile = models.ForeignKey(TalentUser, on_delete=models.CASCADE)

class ProductWishlist(models.Model):
    wishlist_of = models.ForeignKey("user.GeneralUser", on_delete=models.CASCADE, null=True, blank=True)
    wishlist_product = models.ForeignKey("store.Product", on_delete=models.CASCADE)
