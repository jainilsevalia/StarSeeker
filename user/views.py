from rest_framework.exceptions import ParseError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import logout
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.db.models import Q


from .forms import MyLoginForm, MySignupForm
from common.models import SignInCarousel, SignUpCarousel
from .models import (
    GeneralUser,
    TalentImage,
    TalentUser,
    EmbeddedVideo,
    TalentVideo,
    Address,
    State,
    City,
    FAQ,
    Category,
    OtherCountry,
)
from booking.models import Order
from duniyadekhegi.settings import (
    PROFILE_PICTURE_PATH,
    TALENT_PROFILE_CONTENT_IMG_PATH,
    TALENT_PROFILE_CONTENT_VIDEO_PATH,
    USE_S3,
    EMAIL_HOST_USER
)
from duniyadekhegi.utils import delete_django_messages, load_state_city
from allauth.account.views import LoginView, SignupView
from django.contrib.auth.decorators import login_required

from duniyadekhegi.storage_backends import PublicMediaStorage
from booking.utils import talentprofile_created_mail_for_admin

import os
import json
import re
import shortuuid

@login_required(login_url="/", redirect_field_name=None)
def myprofile(request):
    orders = Order.objects.filter(Q(cart__generaluser=request.user) & Q(cart__is_complete=True))
    data = {"orders": orders}
    return render(request, "site/myprofile.html", data)


@login_required(login_url="/", redirect_field_name=None)
def editprofile(request):
    delete_django_messages(request)
    statecitydata, cities = load_state_city()
    addresses = Address.objects.filter(generaluser=request.user).order_by("address")
    otherCountry = OtherCountry.objects.filter(generaluser=request.user).order_by("address")
    data = {
        "statecitydata": statecitydata,
        "cities": cities,
        "addresses": addresses,
        "otherCountry": otherCountry,
    }
    signin_user = request.user
    if "userlink" in request.GET:
        userlink = request.GET["userlink"]
        if not userlink:
            return JsonResponse({"error": "Error: Profile url cannot be empty"})
        else:
            userlinks = GeneralUser.objects.values_list("userlink", flat=True).exclude(pk=signin_user.id)
            isUserLinkExist = False
            for link in userlinks:
                if link == userlink:
                    isUserLinkExist = True
                    break
            if isUserLinkExist:
                return JsonResponse({"error": "Error: Profile url has been taken"})
            else:
                return JsonResponse({"success": 1})

    # FOR PROFILE PICTURE
    try:
        if request.FILES.get("image"):
            signin_user.profile_picture.delete()
            signin_user.save()
            img_obj = request.FILES.get("image", 0)
            img_name = signin_user.userlink + ".png"
            img_path = os.path.join(PROFILE_PICTURE_PATH, img_name)
            if USE_S3:
                fs = PublicMediaStorage()
                fs.save(img_path, img_obj)
            else:
                fs = FileSystemStorage(location=PROFILE_PICTURE_PATH)
                fs.save(img_name, img_obj)
            signin_user.profile_picture = img_path
            signin_user.save()
            return JsonResponse({"success": 1})
    except Exception as e:
        return JsonResponse({"error": "Error: Something went wrong"})

    if "name" in request.POST:
        name = request.POST["name"]
        if not name:
            return JsonResponse({"error": True, "error-msg": "Name is required"})
        phone_number = request.POST["phone_number"]

        if not re.match("^[6-9]\d{9}$", phone_number):
            return JsonResponse({"error": True, "error-msg": "Enter a valid Phone Number"})

        GeneralUser.objects.filter(id=signin_user.id).update(name=name.title(), phone_number=phone_number)
        if "userlink" in request.POST:
            userlink = request.POST["userlink"]
            GeneralUser.objects.filter(id=signin_user.id).update(userlink=userlink)
        return JsonResponse({"success": True})

    if request.method == "DELETE":
        # os.remove(os.path.join(ROOT_PATH, str(signin_user.profile_picture)))
        signin_user.profile_picture.delete()
        signin_user.save()
        return JsonResponse({"success": 1})

    if "email" in request.POST:
        email = request.POST["email"]
        isUserExist = GeneralUser.objects.filter(email=email).exclude(pk=signin_user.id)
        if isUserExist:
            return JsonResponse({"error": "Error: Email already exists"})
        else:
            try:
                validate_email(email)
                signin_user.email = email
                signin_user.save()
                return JsonResponse({"success": True})
            except ValidationError as e:
                return JsonResponse({"error": "Error: Invalid email format"})

    if "oldpassword" in request.POST:
        oldpassword = request.POST["oldpassword"]
        newpassword = request.POST["newpassword"]

        if not oldpassword or not newpassword:
            return JsonResponse({"error": "Error: You have left one of the field empty"})

        if not signin_user.check_password(oldpassword):
            return JsonResponse({"error": "Error: your current password is incorrect"})
        else:
            if oldpassword == newpassword:
                return JsonResponse({"error": "Error: old password and new password can't be same"})

            if len(newpassword) < 8:
                return JsonResponse({"error": "Error: Password must be greater than 8 characters"})
            else:
                signin_user.set_password(newpassword)
                signin_user.save()
                return JsonResponse({"success": 1})

    if "delete_account" in request.GET:
        url = request.build_absolute_uri(
            "/user/deleteaccount/" + urlsafe_base64_encode(force_bytes(signin_user.userlink)) + "/"
        )
        # TODO: Make this part dynamic and use celery task to send mail.
        send_mail(
            "Account delete request from you",
            "Are you sure you want to delete your account on DuniyaDekhegi ? If yes follow below link\n" + url,
            EMAIL_HOST_USER,
            [signin_user.email],
            fail_silently=False,
        )
        return JsonResponse({"success": True})

    if "address" in request.POST:
        try:
            state = request.POST["state"]
            city = request.POST["city"]
            pincode = request.POST["pincode"]
            address = request.POST["address"]

            try:
                state_obj = State.objects.get(name=state)
                city_obj = City.objects.get(name=city)
                AddressModel = Address
            except:
                state_obj = state
                city_obj = city
                AddressModel = OtherCountry

            if request.POST["edit_id"]:
                AddressModel.objects.filter(id=request.POST["edit_id"]).update(
                    state=state_obj, city=city_obj, pincode=pincode, address=address
                )
                return JsonResponse({"success": 1}, status=201)
            else:
                if AddressModel.objects.filter(generaluser=request.user).count() == 0:
                    AddressModel.objects.create(
                        generaluser=request.user,
                        state=state_obj,
                        city=city_obj,
                        pincode=pincode,
                        address=address,
                        is_default=True,
                    )
                else:
                    AddressModel.objects.create(
                        generaluser=request.user, state=state_obj, city=city_obj, pincode=pincode, address=address
                    )
                return JsonResponse({"success": 1}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    if "address_to_set_default" in request.POST:
        try:
            id = request.POST["address_to_set_default"]
            is_other_country = request.POST["is_other_country"]
            if is_other_country:
                AddressModel = OtherCountry
            else:
                AddressModel = Address
            AddressModel.objects.filter(generaluser=request.user, is_default=True).update(is_default=False)
            AddressModel.objects.filter(id=id).update(is_default=True)
            return JsonResponse({"success": 1}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    if "address_to_remove" in request.POST:
        try:
            id = request.POST["address_to_remove"]
            is_other_country = request.POST["is_other_country"]
            if is_other_country:
                AddressModel = OtherCountry
            else:
                AddressModel = Address
            AddressModel.objects.get(id=id).delete()
            return JsonResponse({"success": 1}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, "site/editprofile.html", data)


@login_required(login_url="/", redirect_field_name=None)
def edittalentprofile(request):
    # TODO: solve the image order problem
    talentuser = getattr(request.user, "talentuser", {})
    statecitydata, cities = load_state_city()
    categories = Category.objects.all().values_list("name", flat=True).distinct()

    data = {"talent_images": [], "talent_videos": [], "statecitydata": [], "cities": []}
    talent_images_obj = []
    if talentuser:
        talent_images_obj = TalentImage.objects.filter(talentuser=talentuser)
        talent_images = []
        if talent_images_obj:
            for image in talent_images_obj:
                talent_images.append(image.image.url)
        faqs = FAQ.objects.filter(talentuser=talentuser)
        embedded_videos = EmbeddedVideo.objects.filter(talentuser=talentuser).values_list("embed_video_url", flat=True)
        talent_videos_obj = TalentVideo.objects.filter(talentuser=talentuser)
        talent_videos = []
        if talent_videos_obj:
            for video in talent_videos_obj:
                talent_videos.append(video.video.url)
        data = {
            "talent_images": json.dumps(talent_images),
            "faqs": faqs,
            "embedded_videos": embedded_videos,
            "talent_videos": json.dumps(talent_videos),
        }
    if "talent_category" in request.POST:
        talent_category = request.POST["talent_category"]
        shortdescription = request.POST.get("shortdescription", "")
        other_category = request.POST["other_category"]
        price = request.POST["price"]
        longdescription = request.POST["longdescription"]
        faqs = json.loads(request.POST["faqs"])
        videolinks = json.loads(request.POST["videolinks"])

        gender = request.POST["gender"]
        secondary_skills = request.POST["secondary_skills"].strip()
        engagement = request.POST["engagement"]
        is_trained = request.POST["is_trained"]
        availability = request.POST["availability"].split(',')
        will_travel = request.POST["will_travel"]
        provide_training = request.POST["provide_training"]

        if not shortdescription or not price or not longdescription or not talent_category:
            return JsonResponse({"error": 1, "msg": "You have left one of the field empty"})

        if talent_category == "Other" and not other_category:
            return JsonResponse({"error": 1, "msg": "Please write custom category as you selected other option"})

        if other_category in categories:
            return JsonResponse({"error": 1, "msg": "Category already exists. Please select from dropdown"})


        isNewTalentUser = False
        try:
            talentuser = TalentUser.objects.get(generaluser=request.user)
            TalentImage.objects.filter(talentuser=talentuser).delete()
            TalentVideo.objects.filter(talentuser=talentuser).delete()
        except:
            isNewTalentUser = True
            TalentUser.objects.create(
                generaluser=request.user,
                price=price,
                achievements=shortdescription,
                description=longdescription,
                gender=gender,
                secondary_skills=secondary_skills,
                engagement=engagement,
                is_trained=is_trained,
                availability=availability,
                will_travel=will_travel,
                provide_training=provide_training,
            )

            address = request.POST["address"].strip()
            pincode = request.POST["pincode"].strip()
            city = request.POST["city"]
            state = request.POST["state"]

            if request.POST["is_outside_india"]:
                OtherCountry.objects.create(
                    generaluser=request.user,
                    address=address,
                    pincode=pincode,
                    city=city.capitalize(),
                    state=state.capitalize(),
                    is_default=True,
                )
            else:
                city_obj = City.objects.get(name=city)
                state_obj = State.objects.get(name=state)

                Address.objects.create(
                    generaluser=request.user,
                    address=address,
                    pincode=pincode,
                    city=city_obj,
                    state=state_obj,
                    is_default=True,
                )
            talentuser = get_object_or_404(TalentUser, generaluser=request.user)
            if talent_category == "Other":
                Category.objects.create(talentuser=talentuser, name=other_category)
            else:
                Category.objects.create(talentuser=talentuser, name=talent_category)
        
        files = request.FILES.getlist("files[]")
        thumbnail = ""
        thumbnail_ext = ""
        for index, file in enumerate(files):
            file_name = file.name
            file_ext = file_name.split(".")[1]
            new_name = shortuuid.uuid() + "." + file_ext
            if index == 0:
                thumbnail = new_name
                thumbnail_ext = file_ext
            if file_ext.lower() in ["mp4", "mov", "avi", "webm"]:
                file_loc = os.path.join(TALENT_PROFILE_CONTENT_VIDEO_PATH, request.user.userlink)
                file_path = os.path.join(file_loc, new_name)
                TalentVideo.objects.create(talentuser=talentuser, video=file_path, video_order= index + 1)
            else:
                file_loc = os.path.join(TALENT_PROFILE_CONTENT_IMG_PATH, request.user.userlink)
                file_path = os.path.join(file_loc, new_name)
                TalentImage.objects.create(talentuser=talentuser, image=file_path, image_order= index + 1)
            if USE_S3:
                fs = PublicMediaStorage()
                fs.save(file_path, file)
            else:
                fs = FileSystemStorage(location=file_loc)
                fs.save(new_name, file)
        if thumbnail_ext and thumbnail_ext.lower() in ["mp4", "mov", "avi", "webm"]:
            talentuser.thumbnail = os.path.join(TALENT_PROFILE_CONTENT_VIDEO_PATH, request.user.userlink, thumbnail)
        else:
            talentuser.thumbnail = os.path.join(TALENT_PROFILE_CONTENT_IMG_PATH, request.user.userlink, thumbnail)
        talentuser.save()

        if not isNewTalentUser:
            TalentUser.objects.filter(generaluser__userlink=request.user.userlink).update(
                price=price,
                achievements=shortdescription,
                description=longdescription,
                gender=gender,
                secondary_skills=secondary_skills,
                engagement=engagement,
                is_trained=is_trained,
                availability=availability,
                will_travel=will_travel,
                provide_training=provide_training,
            )
            if talent_category == "Other":
                Category.objects.update_or_create(talentuser=talentuser, defaults={"name": other_category})
            else:
                Category.objects.update_or_create(talentuser=talentuser, defaults={"name": talent_category})
        for faq in faqs:
            if bool(faq) and faq["que"] and faq["ans"]:
                FAQ.objects.update_or_create(talentuser=talentuser, question=faq["que"], answer=faq["ans"])

        EmbeddedVideo.objects.filter(talentuser=talentuser).delete()
        for link in videolinks:
            if bool(link) and link["id"]:
                EmbeddedVideo.objects.create(talentuser=talentuser, embed_video_url=link["id"])

        if isNewTalentUser:
            talentprofile_created_mail_for_admin(talentuser=talentuser)
            return JsonResponse({"success": 1, "msg": "Thank you for registration on DuniyaDekhegi as Talentuser."})
        else:
            return JsonResponse(
                {"success": 1, "msg": "Your public profile has been updated. Redirecting to your public profile..."}
            )


    data["statecitydata"] = statecitydata
    data["cities"] = cities
    data["talent_categories"] = categories
    return render(request, "site/edittalentprofile.html", data)


class MySignupView(SignupView):
    form_class = MySignupForm

    def get_form_class(self):
        return self.form_class

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        carousel = SignUpCarousel.objects.all().order_by("carousel_order")
        context["carousel"] = carousel
        return context


class MyLoginView(LoginView):
    form_class = MyLoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        carousel = SignInCarousel.objects.all().order_by("carousel_order")
        context["carousel"] = carousel
        return context

    def get_form_class(self):
        return self.form_class


def signout(request):
    logout(request)
    return redirect("home")


def deleteaccount(request, userlink):
    decoded_userlink = force_text(urlsafe_base64_decode(userlink))
    account_holder = get_object_or_404(GeneralUser, userlink=decoded_userlink)
    data = {
        "account_holder": account_holder,
    }
    if "confirmdelete" in request.GET:
        isTalentUser = TalentUser.objects.filter(generaluser__userlink=decoded_userlink)
        if isTalentUser:
            isTalentUser.delete()
        account_holder.delete()
        return JsonResponse({"success": 1})
    return render(request, "site/deleteaccount.html", data)

@login_required
def onboarding(request):
    return render(request, "site/onboarding.html")
