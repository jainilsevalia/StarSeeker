from django.db import models
from multiselectfield import MultiSelectField


class Cart(models.Model):
    generaluser = models.ForeignKey(
        'user.GeneralUser', on_delete=models.SET_NULL, null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=150, default=0)
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0)
    date_ordered = models.DateTimeField(auto_now=True)
    address = models.CharField(max_length=150, blank=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    pincode = models.CharField(max_length=15, blank=True)
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0)

    @property
    def cart_items(self):
        cart_items = self.cartitem_set.all()
        return cart_items

    @property
    def cart_total(self):
        cartitems = self.cartitem_set.all()
        total = sum([item.sub_total for item in cartitems])
        return total

    @property
    def cart_item_count(self):
        items = self.cartitem_set.count()
        return items


class CartItem(models.Model):
    SLOT_CHOICES = (
        ('Morning', 'Morning'),
        ('Afternoon', 'Afternoon'),
        ('Evening', 'Evening'),
        ('Night', 'Night'),
    )
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True)
    talentuser = models.ForeignKey(
        'user.TalentUser', on_delete=models.SET_NULL, null=True, blank=True)
    number_of_days = models.IntegerField(null=True, blank=True, default=1)
    start_date = models.DateField()
    slot_of_day = MultiSelectField(
        choices=SLOT_CHOICES, max_choices=3, blank=True)
    event_type = models.CharField(max_length=50, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def sub_total(self):
        return self.talentuser.price * self.number_of_days

    def __str__(self):
        return str(self.cart.id) + self.talentuser.generaluser.name if self.cart else "-"


class Order(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True)
