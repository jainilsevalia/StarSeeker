from django.core.exceptions import ValidationError
from django.core.validators import validate_email, URLValidator
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.db.models import Q

# from django.template.loader import render_to_string

from .models import Carousel, Comment, Survey
from user.models import (
    GeneralUser,
    TalentUser,
    TalentImage,
    TalentVideo,
    EmbeddedVideo,
    FAQ,
    Wishlist,
    State,
    City,
    Category,
)
from booking.models import CartItem
from duniyadekhegi.utils import delete_django_messages, load_state_city
from datetime import datetime
from user.tasks import send_email_from_celery, send_templated_email_celery
from duniyadekhegi.settings import EMAIL_HOST_USER;

import re


def home(request):
    delete_django_messages(request)
    statecitydata, cities = load_state_city()
    carousel = Carousel.objects.all().order_by("carousel_order")
    categories = Category.objects.all().values_list("name", flat=True).distinct()
    talentusers = TalentUser.objects.all()
    data = {
        "carousel": carousel,
        "talentusers": talentusers,
        "talent_categories": categories,
        "statecitydata": statecitydata,
        "cities": cities,
    }
    return render(request, "site/home.html", data)


def talentprofile(request, userlink):
    talentuser = get_object_or_404(TalentUser, generaluser__userlink=userlink)

    if request.user.is_authenticated:
        if getattr(request.user, 'talentuser', None) != talentuser and not talentuser.is_kyc_done:
            return redirect('home')
    else:
        if not talentuser.is_kyc_done:
            return redirect('home')

    talentImages = TalentImage.objects.filter(talentuser__generaluser__userlink=userlink)
    talentVideos = TalentVideo.objects.filter(talentuser__generaluser__userlink=userlink)
    embeddedVideos = EmbeddedVideo.objects.filter(talentuser__generaluser__userlink=userlink)
    faqs = FAQ.objects.filter(talentuser__generaluser__userlink=userlink)
    try:
        cart_item_profiles = CartItem.objects.filter(cart=request.user.user_cart).values_list("talentuser", flat=True)
    except:
        cart_item_profiles = None

    wishlist = None
    if request.user.is_authenticated:
        try:
            wishlist = Wishlist.objects.get(wishlist_of=request.user, wishlist_profile=talentuser)
        except Wishlist.DoesNotExist:
            wishlist = None

    comments = Comment.objects.filter(comment_for=talentuser.id).order_by("timestamp")
    try:
        user_review = Comment.objects.get(comment_by=request.user.id, comment_for=talentuser.id)
    except Comment.DoesNotExist:
        user_review = None

    review_chart_data = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    total_comments = len(comments)
    for comment in comments:
        n = comment.rating
        review_chart_data[n] += 1
    if total_comments:
        for k, v in review_chart_data.items():
            review_chart_data[k] = 100 * (v / total_comments)
    data = {
        "talentuser": talentuser,
        "talentImages": talentImages,
        "talentVideos": talentVideos,
        "embeddedVideos": embeddedVideos,
        "faqs": faqs,
        "comments": comments,
        "user_review": user_review,
        "inUserwishlist": wishlist,
        "review_chart_data": review_chart_data,
        "cart_item_profiles": cart_item_profiles,
    }
    if "comment" in request.POST:
        form_comment = request.POST.get("comment", "")
        form_rating = int(request.POST.get("rating", 0))
        comment_by = get_object_or_404(GeneralUser, pk=request.user.id)
        comment_for = get_object_or_404(TalentUser, pk=talentuser.id)
        timestamp = datetime.now()

        if not user_review:
            review = Comment.objects.create(
                comment_by=comment_by,
                comment_for=comment_for,
                comment=form_comment,
                timestamp=timestamp,
                rating=form_rating,
            )
            review.save()
            return JsonResponse({"save_review": "Review added"})
        else:
            user = Comment.objects.get(comment_by=request.user.id)
            if user.comment == form_comment and user.rating == form_rating:
                pass
            elif user.comment == form_comment and user.rating != form_rating:
                if form_rating == "":
                    Comment.objects.filter(comment_by=request.user.id).update(rating=0)
                else:
                    Comment.objects.filter(comment_by=request.user.id).update(rating=form_rating)
                    return JsonResponse({"updated_rating": "Rating updated"})
            elif user.comment != form_comment and user.rating == form_rating:
                if form_comment == "":
                    Comment.objects.filter(comment_by=request.user.id).delete()
                else:
                    Comment.objects.filter(comment_by=request.user.id).update(comment=form_comment)
                    return JsonResponse({"updated_comment": "Comment updated"})
            else:
                Comment.objects.filter(comment_by=request.user.id).update(comment=form_comment, rating=form_rating)
                return JsonResponse({"updated_review": "Review updated"})

    if "addtowishlist" in request.GET:
        wishlist_profile = get_object_or_404(TalentUser, pk=request.GET["addtowishlist"])
        wishlist_item = Wishlist.objects.create(wishlist_of=request.user, wishlist_profile=wishlist_profile)
        wishlist_item.save()
        return JsonResponse({"success": 1})

    if "cart_talentuser_id" in request.POST:
        cart = request.user.user_cart
        cart_talentuser_id = request.POST["cart_talentuser_id"]
        talentuser = get_object_or_404(TalentUser, pk=cart_talentuser_id)
        start_date = datetime.today().strftime("%Y-%m-%d")
        cart_item = CartItem.objects.create(cart=cart, talentuser=talentuser, start_date=start_date)
        cart_item.save()
        return JsonResponse({"success": 1})

    return render(request, "site/talentprofile.html", data)


def filter(request):
    if "state_search" in request.POST:
        state_search = request.POST.get("state_search")
        city_search = request.POST.getlist("city_search[]")
        rating_search = request.POST.get("rating_search")
        price_search = request.POST.get("price_search")
        category_search = request.POST.get("category_search")
        wishlist_search = request.POST.get("wishlist_search")
        keyword = request.POST.get("keyword")

        if keyword:
            talentusers = TalentUser.objects.filter(
                Q(generaluser__name__icontains=keyword)
                | Q(description__icontains=keyword)
                | Q(achievements__icontains=keyword)
                | Q(category__name__icontains=keyword)
                | Q(generaluser__address__state__name__icontains=keyword)
                | Q(generaluser__address__city__name__icontains=keyword)
            )
        else:
            talentusers = TalentUser.objects.all()

        categories = Category.objects.all().values_list("name", flat=True).distinct()
        if wishlist_search == "true":
            wishlist_profiles = request.user.wishlist_set.values_list("wishlist_profile__id", flat=True)
            talentusers = talentusers.filter(id__in=wishlist_profiles)
        if category_search != "all":
            talentusers = talentusers.filter(category__name__icontains=category_search)
        if state_search:
            talentusers = talentusers.filter(generaluser__address__state__name=state_search)
        if city_search:
            talentusers = talentusers.filter(generaluser__address__city__name__in=city_search)
        if price_search:
            min_price_search, max_price_search = (i for i in price_search.split("-"))
            talentusers = talentusers.filter(Q(price__gte=min_price_search) & Q(price__lte=max_price_search))
        if rating_search:
            talentusers = [t for t in talentusers if t.rating_avg >= int(rating_search)]

        data = {"talentusers": talentusers, "talent_categories": categories}
        return render(request, "includes/searchtalentuser.html", data)


def search(request):
    talentusers = TalentUser.objects.all()
    categories = Category.objects.all().values_list("name", flat=True).distinct()
    statecitydata, cities = load_state_city()
    data = {
        "talentusers": talentusers,
        "statecitydata": statecitydata,
        "cities": cities,
        "talent_categories": categories,
    }
    if "keyword" in request.POST and request.POST["keyword"]:
        keyword = request.POST["keyword"]
        data["keyword"] = keyword
        tprofile = TalentUser.objects.filter(
            Q(generaluser__name__icontains=keyword)
            | Q(description__icontains=keyword)
            | Q(achievements__icontains=keyword)
            | Q(category__name__icontains=keyword)
            | Q(generaluser__address__state__name__icontains=keyword)
            | Q(generaluser__address__city__name__icontains=keyword)
        )
        data["talentusers"] = tprofile

    return render(request, "site/searchresult.html", data)


# Helper method for survey


def url_validator(url):
    url_validate = URLValidator(["https"])
    try:
        if url:
            url_validate(url)
    except ValidationError as e:
        url_of = url.split("_")[0]
        return JsonResponse({"error": 1, "msg": "Invalid {} profile url.".format(url_of)})


def survey(request):
    statecitydata, cities = load_state_city()
    data = {
        "statecitydata": statecitydata,
        "cities": cities,
    }
    if "primary_skill" in request.POST:
        name = request.POST["name"].strip()
        email = request.POST["email"].strip()
        phone_number = request.POST["phone_number"].strip()
        gender = request.POST["gender"]
        description = request.POST["description"].strip()
        primary_skill = request.POST["primary_skill"]
        primary_skill_other = request.POST["primary_skill_other"].strip()
        secondary_skills = request.POST["secondary_skills"].strip()
        engagement = request.POST["engagement"]
        is_trained = request.POST["is_trained"]
        availability = request.POST.getlist("availability[]", "")
        address = request.POST["address"].strip()
        pincode = request.POST["pincode"].strip()
        city = request.POST["city"]
        state = request.POST["state"]
        will_travel = request.POST["will_travel"]
        provide_training = request.POST["provide_training"]
        price = request.POST["price"].strip()
        price_rate = request.POST["price_rate"]
        instagram_url = request.POST["instagram_url"].strip()
        facebook_url = request.POST["facebook_url"].strip()
        youtube_url = request.POST["youtube_url"].strip()
        twitter_url = request.POST["twitter_url"].strip()

        if (
            not name
            or not email
            or not gender
            or not description
            or not primary_skill
            or not engagement
            or not is_trained
            or not availability
            or not address
            or not pincode
            or not city
            or not state
            or not will_travel
            or not provide_training
        ):
            return JsonResponse({"error": 1, "msg": "You have left one of the mandatory field empty."})

        if city and state:
            city_obj = City.objects.get(name=city)
            state_obj = State.objects.get(name=state)

        if primary_skill == "Other" and not primary_skill_other:
            return JsonResponse({"error": 1, "msg": "Please write your primary skill."})

        if phone_number and not re.match("^[6-9]\d{9}$", phone_number):
            return JsonResponse({"error": 1, "msg": "Enter a valid Phone Number"})

        try:
            validate_email(email)
        except ValidationError as e:
            return JsonResponse({"error": 1, "msg": "Invalid email format."})

        url_validator(instagram_url)
        url_validator(facebook_url)
        url_validator(youtube_url)
        url_validator(twitter_url)

        isEmailExists = Survey.objects.filter(email=email)
        if isEmailExists:
            Survey.objects.update(
                name=name,
                phone_number=phone_number,
                gender=gender,
                description=description,
                primary_skill=primary_skill,
                secondary_skills=secondary_skills,
                engagement=engagement,
                is_trained=is_trained,
                availability=availability,
                address=address,
                pincode=pincode,
                city=city_obj,
                state=state_obj,
                will_travel=will_travel,
                provide_training=provide_training,
                price=price,
                price_rate=price_rate,
                instagram_url=instagram_url,
                facebook_url=facebook_url,
                youtube_url=youtube_url,
                twitter_url=twitter_url,
            )
        else:
            Survey.objects.create(
                email=email,
                name=name,
                phone_number=phone_number,
                gender=gender,
                description=description,
                primary_skill=primary_skill,
                primary_skill_other=primary_skill_other,
                secondary_skills=secondary_skills,
                engagement=engagement,
                is_trained=is_trained,
                availability=availability,
                address=address,
                pincode=pincode,
                city=city_obj,
                state=state_obj,
                will_travel=will_travel,
                provide_training=provide_training,
                price=price,
                price_rate=price_rate,
                instagram_url=instagram_url,
                facebook_url=facebook_url,
                youtube_url=youtube_url,
                twitter_url=twitter_url,
            )
        availability_str = ",".join(availability)
        email_data = {
            "name": name,
            "email": email,
            "phone_number": phone_number,
            "gender": gender,
            "description": description,
            "primary_skill": primary_skill,
            "primary_skill_other": primary_skill_other if primary_skill_other else "",
            "secondary_skills": secondary_skills,
            "engagement": engagement,
            "is_trained": "Yes" if is_trained else "No",
            "availability": availability_str,
            "address": address,
            "pincode": pincode,
            "city": city,
            "state": state,
            "will_travel": "Yes" if will_travel else "No",
            "provide_training": "Yes" if provide_training else "No",
            "price": price,
            "price_rate": price_rate,
            "instagram_url": instagram_url if instagram_url else "-",
            "facebook_url": facebook_url if facebook_url else "-",
            "youtube_url": youtube_url if youtube_url else "-",
            "twitter_url": twitter_url if twitter_url else "-",
        }
        send_templated_email_celery(
            {
                "template_name": "survey",
                "from_email": EMAIL_HOST_USER,
                "recipient_list": [email],
                "context": email_data,
            }
        )
        return JsonResponse({"success": 1})

    return render(request, "site/survey.html", data)


def sendemailtotalentuser():
    talent_emails = list(TalentUser.objects.all().values_list("generaluser__email", flat=True))
    send_templated_email_celery(
        {
            "template_name": "pre-registered",
            "from_email": EMAIL_HOST_USER,
            "recipient_list": talent_emails,
            "context": {},
        }
    )
    return JsonResponse({"success": 1})


# Methods for footers
def blogs(request):
    return render(request, "site/blogs.html")


def contactus(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        contact = request.POST["contact"]
        message = request.POST["message"]

        if not name or not email or not message:
            return JsonResponse(
                {
                    "error": 1,
                    "error-msg": "You have left one of the mandatory field empty.",
                }
            )

        try:
            validate_email(email)
        except ValidationError as e:
            return JsonResponse({"error": 1, "error-msg": "Invalid email format."})

        if not re.match("^[6-9]\d{9}$", contact):
            return JsonResponse({"error": 1, "error-msg": "Enter a valid Phone Number"})

        admins = list(GeneralUser.objects.filter(is_superuser=True).values_list("email", flat=True))
        subject = name + " want to say something about DuniyaDekhegi"
        body = "\n\n" + message + "\n\nEmail of user: " + email + "\nContact: " + contact
        data = {"email_subject": subject, "email_body": body, "to_email": admins}
        send_email_from_celery.delay(data)
        return JsonResponse({"success": 1, "success-msg": "Successfully sent your message"})

    return render(request, "site/contactus.html")


def reportbug(request):
    return render(request, "site/reportbug.html")


def about(request):
    return render(request, "site/about.html")


def support(request):
    return render(request, "site/support.html")


def termsofservice(request):
    return render(request, "site/termsofservice.html")


def privacypolicy(request):
    return render(request, "site/privacypolicy.html")


def bookvenue(request):
    return render(request, "site/bookvenue.html")


def advertisement(request):
    return render(request, "site/advertisement.html")


def brandcollaboration(request):
    return render(request, "site/brandcollaboration.html")
