from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from user.tasks import send_templated_email_celery
from .models import (
    GeneralUser,
    OtherCountry,
    ProductWishlist,
    Seller,
    UserLogin,
    TalentUser,
    TalentImage,
    TalentVideo,
    EmbeddedVideo,
    FAQ,
    Wishlist,
    State,
    City,
    Address,
    Category,
)

# from django.contrib.admin import SimpleListFilter
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import path, reverse
from django.contrib import messages
from duniyadekhegi.settings import EMAIL_HOST_USER;

admin.site.register(Wishlist)


@admin.register(UserLogin)
class UserAdmin(admin.ModelAdmin):
    list_display = ("generaluser_email", "timestamp")

    def generaluser_email(self, obj):
        return obj.generaluser.email


# class TalentFilter(SimpleListFilter):
#     title = 'Talent Filter'
#     parameter_name = 'talent_category'

#     def lookups(self, request, model_admin):
#         return(
#             ('Singer', 'Singer'),
#             ('Dancer', 'Dancer'),
#             ('Actor', 'Actor'),
#             ('Voice Artist', 'Voice Artist'),
#             ('Comedian', 'Comedian'),
#             ('Writer', 'Writer'),
#             ('Model', 'Model'),
#         )

#     def queryset(self, request, queryset):
#         if self.value():
#             return queryset.filter(talent_category__icontains=self.value())


class AddressInline(admin.TabularInline):
    extra = 1
    model = Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("state", "city", "address", "pincode", "generaluser")
    autocomplete_fields = ["state", "city"]

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    ordering = [
        "name",
    ]
    search_fields = ("name",)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    ordering = ["state__name", "name"]
    search_fields = ("name",)
    autocomplete_fields = ["state"]


@admin.register(OtherCountry)
class OtherCountryAdmin(admin.ModelAdmin):
    list_display = ("address", "pincode", "state", "city", "is_default")
    list_filter = ("state", "city")

class OtherCountryInline(admin.TabularInline):
    extra = 1
    model = OtherCountry

@admin.register(GeneralUser)
class GeneralUserAdmin(UserAdmin):
    inlines = [AddressInline, OtherCountryInline]
    list_display = ("name", "email", "phone_number", "login_count", "is_superuser")
    list_filter = ("is_admin",)
    fieldsets = (
        (None, ({"fields": ("name", "email", "password", "is_verified")})),
        ("Personal Details", ({"fields": ("userlink", "profile_picture", "phone_number")})),
        ("Permissions", ({"fields": ("is_admin", "is_staff", "groups")})),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "name", "password1", "password2"),
            },
        ),
    )
    ordering = ("email",)

    # for action to send selected users a custom mail 
    actions = ["send_mail"]
    def send_mail(self, request, queryset):
        if "send" in request.POST:
            print("inside post request")
            subject = request.POST["subject"]
            heading = request.POST["heading"]
            message = request.POST["message"]

            email_data = {
                "subject": subject,
                "heading": heading,
                "message": message,
                "from_email": EMAIL_HOST_USER,
            }
            for user in queryset:
                send_templated_email_celery(
                    {
                        "template_name": "custom-email",
                        "from_email": EMAIL_HOST_USER,
                        "recipient_list": [user.email],
                        "context": email_data,
                    }
                )
            return HttpResponseRedirect(request.get_full_path())
        context = dict(self.admin_site.each_context(request))
        context["users"] = queryset
        return render(request, 'admin/send-mail.html', context=context)
    
    send_mail.short_description = "Send email to selected users"
class TalentImageInline(admin.TabularInline):
    extra = 1
    model = TalentImage
    fields = (
        "image",
        "image_order",
        "image_tag",
    )
    readonly_fields = ("image_tag",)
    ordering = ("image_order",)

    def image_tag(self, obj):
        from django.utils.html import mark_safe

        return mark_safe('<img src="%s" width="150" height="150" />' % (obj.image.url))

    image_tag.short_description = "Image"
    image_tag.allow_tags = True


class TalentVideoInline(admin.TabularInline):
    extra = 1
    model = TalentVideo
    fields = (
        "video",
        "video_order",
        "video_tag",
    )
    readonly_fields = ("video_tag",)
    ordering = ("video_order",)

    def video_tag(self, obj):
        from django.utils.html import mark_safe

        return mark_safe('<video width="150" height="150" ><source src="%s"/></video>' % (obj.video.url))

    video_tag.short_description = "Video"
    video_tag.allow_tags = True


class EmbeddedVideoInline(admin.TabularInline):
    extra = 1
    model = EmbeddedVideo
    fields = ("embed_video_url",)
    # readonly_fields = ('embed_video_tag',)
    # ordering = ('embeded_video_order',)

    def embed_video_tag(self, obj):
        from django.utils.html import mark_safe

        return mark_safe(
            '<iframe src="%s"  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen width="150" height="150" ></iframe>'
            % (obj.embed_video_url)
        )

    embed_video_tag.short_description = "Embed-Video"
    embed_video_tag.allow_tags = True


class FAQInline(admin.TabularInline):
    extra = 1
    model = FAQ


class CategoryInline(admin.TabularInline):
    extra = 1
    model = Category


@admin.register(TalentUser)
class TalentUserAdmin(admin.ModelAdmin):
    inlines = [TalentImageInline, TalentVideoInline, EmbeddedVideoInline, FAQInline, CategoryInline]
    list_display = ("name", "email", "category","date_created", "last_login", "is_kyc_done", "action")
    search_fields = (
        "generaluser__name",
        "generaluser__email",
    )
    readonly_fields = (
        "date_created",
        "last_login",
    )
    list_filter = (
        "generaluser__last_login",
        "generaluser__date_created",
    )

    def KYC(self, obj):
        return obj.generaluser.is_kyc_done

    KYC.short_description = "KYC"
    KYC.boolean = True

    def date_created(self, obj):
        return obj.generaluser.date_created.strftime("%d %b %Y")

    date_created.admin_order_field = "date_created"
    date_created.short_description = "Date Created"

    def last_login(self, obj):
        if obj.generaluser.last_login:
            return obj.generaluser.last_login.strftime("%d %b %Y")
        return None

    last_login.admin_order_field = "last_login"
    last_login.short_description = "Last Login"


    # APPROVE KYC FUNCTIONALITY 
    def get_urls(self):
        urls = super().get_urls()
        custom_urls  = [
            path('approve-kyc/<int:id>/', self.admin_site.admin_view(self.approve_kyc), name="approve-kyc"),

        ]
        return custom_urls + urls
    
    def approve_kyc(self, request, id):
        talentuser = get_object_or_404(TalentUser, id=id)
        talentuser.is_kyc_done = True
        talentuser.save()
        email_data = {
            "userlink": request.scheme + "://" + request.get_host() + reverse('talentprofile', args=[talentuser.generaluser.userlink]),
            "from_email": EMAIL_HOST_USER,
        }
        send_templated_email_celery(
            {
                "template_name": "kyc-approve",
                "from_email": EMAIL_HOST_USER,
                "recipient_list": [talentuser.generaluser.email],
                "context": email_data,
            }
        )
        messages.success(request, "{} 's kyc has been approved and email has been sent to {}".format(talentuser.generaluser.name, "him" if talentuser.gender == 'male' else "her"))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def action(self, obj):
        if not obj.is_kyc_done:
            return format_html('<a class="button" href="{}">Approve</a>', reverse('admin:approve-kyc', args=[obj.id]))
    class Meta:
        model = TalentUser


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "talentuser", "talentuser_name")

    def talentuser_name(self, obj):
        return obj.talentuser.name if obj.talentuser else "-"


@admin.register(TalentImage)
class TalentImageAdmin(admin.ModelAdmin):
    list_display = ("talentuser", "upload_date")
    list_filter = ("upload_date",)


@admin.register(TalentVideo)
class TalentVideoAdmin(admin.ModelAdmin):
    list_display = ("talentuser", "upload_date")
    list_filter = ("upload_date",)


@admin.register(EmbeddedVideo)
class EmbeddedVideoAdmin(admin.ModelAdmin):
    list_display = ("talentuser", "upload_date")
    list_filter = ("upload_date",)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("talentuser", "upload_date")
    list_filter = ("upload_date",)

@admin.register(ProductWishlist)
class ProductWishlistAdmin(admin.ModelAdmin):
    list_display = (
        "wishlist_of",
        "wishlist_product",
    )

    def wishlist_of(self, obj):
        return obj.wishilist_of.email

    def wishlist_product(self, obj):
        return obj.wishlist_product.name

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ("seller", "store_name", "timestamp", "is_kyc_done", "action")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls  = [
            path('approve-kyc-store/<int:id>/', self.admin_site.admin_view(self.approve_kyc_store), name="approve-kyc-store")
        ]
        return custom_urls + urls
    
    def approve_kyc_store(self, request, id):
        seller = get_object_or_404(Seller, id=id)
        seller.is_kyc_done = True
        seller.save()
        email_data = {
            "storelink": request.scheme + "://" + request.get_host() + reverse('personal_store', args=[seller.id]),
            "from_email": EMAIL_HOST_USER,
        }
        send_templated_email_celery(
            {
                "template_name": "kyc-approve-store",
                "from_email": EMAIL_HOST_USER,
                "recipient_list": [seller.generaluser.email],
                "context": email_data,
            }
        )
        messages.success(request, "{} 's kyc has been approved and email has been sent".format(seller.generaluser.email))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def action(self, obj):
        if not obj.is_kyc_done:
            return format_html('<a class="submit-row" href="{}"><input type="button" value="Approve" /></a>', reverse('admin:approve-kyc-store', args=[obj.id]))
    
    def seller(self, obj):
        return obj.generaluser.email