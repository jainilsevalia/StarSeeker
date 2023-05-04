from django.db import models
from django.template.defaultfilters import slugify
from statistics import mean
from django.core.validators import MinValueValidator, MaxValueValidator
from duniyadekhegi.settings import USER_STORE_IMG_PATH

class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        self.name = self.name.upper()
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, blank=True, null=True)
    added_by = models.ForeignKey("user.Seller", on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(null=True)
    slug = models.SlugField(max_length=50, blank=True, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    thumbnail = models.FileField(upload_to=USER_STORE_IMG_PATH, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        import uuid

        uniquechars = str(uuid.uuid4())[-10:]
        if self.slug:
            prev_slug = "-".join(self.slug.split("-")[:-1])
            if not slugify(self.name) == prev_slug:
                self.slug = slugify(self.name + " " + uniquechars)
        else:
            self.slug = slugify(self.name + " " + uniquechars)
        super(Product, self).save(*args, **kwargs)

    @property
    def rating(self):
        review_query_set = self.review_set.all()
        rating = 0
        try:
            ratings_set = [x.rating for x in review_query_set]
            rating = round(mean(ratings_set), 1)
        except:
            pass
        return rating

    @property
    def times_ordered(self):
        orders = StoreOrderItem.objects.filter(product=self).values_list("order", flat=True).distinct()
        completed = StoreOrder.objects.filter(id__in=orders, is_complete=True).count()
        return completed

    @property
    def media(self):
        images = list(ProductImage.objects.filter(product=self).values_list("image", flat=True))
        videos = list(ProductVideo.objects.filter(product=self).values_list("video", flat=True))
        return { "images": images, "videos": videos }

    def isVideoThumbnail(self):
        return True if any(ext in self.thumbnail.url for ext in [".mp4", ".mov", ".avi", ".webm"]) else False

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=USER_STORE_IMG_PATH, null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    def delete(self, using=None, keep_parents=False):
        self.image.storage.delete(self.image.name)
        super().delete()

class ProductVideo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    video = models.FileField(upload_to=USER_STORE_IMG_PATH, null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    def delete(self, using=None, keep_parents=False):
        self.video.storage.delete(self.video.name)
        super().delete()

class StoreOrder(models.Model):
    PAYMENT_STATUSES = ((1, "SUCCESS"), (2, "FAILURE"), (3, "PENDING"))
    user = models.ForeignKey("user.GeneralUser", on_delete=models.SET_NULL, null=True)
    is_complete = models.BooleanField(default=False)
    payment_status = models.IntegerField(choices=PAYMENT_STATUSES, default=3)
    order_id = models.CharField(max_length=100, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)
    address_line = models.CharField(max_length=150, blank=True, null=True)
    state = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=100, null=True)
    pincode = models.CharField(max_length=10, null=True)

    razorpay_order_id = models.CharField(max_length=50, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=50, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=500, null=True, blank=True)

    @property
    def get_cart_total(self):
        cart_items = self.cartitem.all()
        total = sum([item.get_total for item in cart_items])
        return total

    @property
    def get_cart_items_count(self):
        return self.cartitem.count()

    @property
    def get_cart_items_quantity(self):
        cart_items = self.cartitem.all()
        quantity = sum([item.quantity for item in cart_items])
        return quantity

    def save(self, *args, **kwargs):
        if self.order_id is None and self.date_ordered and self.id:
            self.order_id = str(self.date_ordered.strftime("#DDES%Y%m%d")) + str(self.id)
        return super().save(*args, **kwargs)

class StoreOrderItem(models.Model):
    order = models.ForeignKey("StoreOrder", on_delete=models.SET_NULL, null=True, blank=True, related_name="cartitem")
    product = models.ForeignKey("Product", on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        return self.product.price * self.quantity

class RecommendedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rank = models.IntegerField()

class Review(models.Model):
    customer = models.ForeignKey("user.GeneralUser", on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=50, blank=True, null=True)
    detail = models.CharField(max_length=350, null=True, blank=True)

    class Meta:
        unique_together = ["customer", "product"]

