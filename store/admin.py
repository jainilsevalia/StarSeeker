from django.contrib import admin

from user.models import GeneralUser
from .models import Category, Product, RecommendedProduct, StoreOrder, StoreOrderItem, ProductImage, ProductVideo


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


class ProductImageInline(admin.TabularInline):
    extra = 1
    model = ProductImage
    fields = (
        "image",
        "image_tag",
    )
    readonly_fields = ("image_tag",)

    def image_tag(self, obj):
        from django.utils.html import mark_safe

        return mark_safe('<img src="%s" width="150" height="150" />' % (obj.image.url))

    image_tag.short_description = "Image"
    image_tag.allow_tags = True


class ProductVideoInline(admin.TabularInline):
    extra = 1
    model = ProductVideo
    fields = (
        "video",
        "video_tag",
    )
    readonly_fields = ("video_tag",)

    def video_tag(self, obj):
        from django.utils.html import mark_safe

        return mark_safe('<video width="150" height="150" ><source src="%s"/></video>' % (obj.video.url))

    video_tag.short_description = "Video"
    video_tag.allow_tags = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductVideoInline]
    list_display = ("name", "price", "rating")
    exclude = ["slug"]
    autocomplete_fields = ("category",)


@admin.register(RecommendedProduct)
class RecommendedProductAdmin(admin.ModelAdmin):
    list_display = ("product_name", "rank")

    def product_name(self, obj):
        return obj.product.name

class StoreOrderItemInline(admin.TabularInline):
    model = StoreOrderItem
    extra = 0
    can_delete = False
    fields = ["product_details", "quantity"]
    readonly_fields = ["product_details", "quantity"]

    def product_details(self, obj):
        return obj.product.name + " - (" + obj.product.added_by.generaluser.name + ")"


@admin.register(StoreOrder)
class StoreOrderAdmin(admin.ModelAdmin):
    list_display = ("user__name", "amount", "payment_status", "is_complete", "date_ordered")
    search_fields = ("order_id", "razorpay_order_id", "razorpay_payment_id", "user__name")
    inlines = [StoreOrderItemInline]

    def user__name(self, obj):
        return GeneralUser.objects.get(id=obj.user.id).name


@admin.register(StoreOrderItem)
class StoreOrderItemAdmin(admin.ModelAdmin):
    pass
