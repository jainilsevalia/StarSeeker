from django.contrib import admin
from .models import Carousel, SignInCarousel, SignUpCarousel, Comment, Survey


@admin.register(Carousel)
class CarouselAdmin(admin.ModelAdmin):
    list_display = ('title', 'carousel_order',
                    'upload_date', 'image_tag')
    list_filter = ('upload_date',)

    def image_tag(self, obj):
        from django.utils.html import mark_safe
        return mark_safe('<img src="%s" width="50" height="50" />' % (obj.image.url))
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment_by', 'comment_for',
                    'rating', 'timestamp')


@admin.register(SignInCarousel)
class SignInCarouselAdmin(admin.ModelAdmin):
    list_display = ('carousel_order', 'image_tag',
                    'upload_date')
    list_filter = ('upload_date',)

    def image_tag(self, obj):
        from django.utils.html import mark_safe
        return mark_safe('<img src="%s" width="50" height="50" />' % (obj.image.url))
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True


@admin.register(SignUpCarousel)
class SignUpCarouselAdmin(admin.ModelAdmin):
    list_display = ('carousel_order', 'image_tag',
                    'upload_date')
    list_filter = ('upload_date',)

    def image_tag(self, obj):
        from django.utils.html import mark_safe
        return mark_safe('<img src="%s" width="50" height="50" />' % (obj.image.url))
    image_tag.short_description = 'Image'
    image_tag.allow_tags = True


admin.site.register(Survey)
