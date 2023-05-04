from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .models import Order, CartItem, Cart
from user.models import TalentUser, State, City
from booking.utils import send_order_completion_mails
from store.utils import cartData

import json
import shortuuid


@login_required(login_url='/', redirect_field_name=None)
def cart(request):
    cartitems = CartItem.objects.filter(cart=request.user.user_cart)
    statecitydata = {}
    states = State.objects.values_list(
        'name', flat=True).order_by('name')
    product_data = cartData(request)

    cities = []
    for state in states:
        state_cities = list(City.objects.filter(state__name=state).values_list(
            'name', flat=True).order_by('name'))
        statecitydata[state] = state_cities
        cities.extend(state_cities)
    data = {
        "cartitems": cartitems,
        "statecitydata": statecitydata,
        "cities": cities,
        "items": product_data["items"], 
        "order":product_data["order"], 
        "cartItems":product_data["cartItems"],
        "categories": product_data["categories"],
    }
    if 'tuserlink' in request.POST:
        tuserlink = request.POST['tuserlink']
        talentuser = get_object_or_404(
            TalentUser, generaluser__userlink=tuserlink)
        CartItem.objects.filter(
            cart=request.user.user_cart, talentuser=talentuser).delete()
        return JsonResponse({"success": 1})

    if 'talentusersDetails' in request.POST:
        talentuser_details = json.loads(request.POST['talentusersDetails'])
        personal_deatils = json.loads(request.POST['personalDetails'])
        total_amount = request.POST.get("total_amount")

        for tuser in talentuser_details:
            talentuser = get_object_or_404(
                TalentUser, generaluser__userlink=tuser)
            tuser = talentuser_details[tuser]
            start_date = tuser["event_date"]
            event_type = tuser["event_type"]
            slot_of_day = tuser["slot_of_the_day"]
            number_of_days = tuser["no_of_days"]

            CartItem.objects.filter(
                cart=request.user.user_cart, talentuser=talentuser).update(start_date=start_date, event_type=event_type, slot_of_day=slot_of_day, number_of_days=number_of_days)

        state = personal_deatils["state"]
        city = personal_deatils["city"]
        pincode = personal_deatils["pincode"]
        address = personal_deatils["address"]
        transaction_id = shortuuid.uuid()
        Cart.objects.filter(generaluser=request.user, is_complete=False).update(
            is_complete=True, transaction_id=transaction_id, state=state, city=city, pincode=pincode, address=address, total_amount=total_amount)
        cart = get_object_or_404(Cart, transaction_id=transaction_id)
        send_order_completion_mails(cart=cart)
        Order.objects.create(cart=cart)
        return JsonResponse({"success": 1})
    return render(request, 'site/cart.html', data)
