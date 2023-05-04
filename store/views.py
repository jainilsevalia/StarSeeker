from django.shortcuts import get_object_or_404, redirect, render
from .models import (
    ProductImage,
    ProductVideo,
    RecommendedProduct,
    Product,
    Category,
    Review,
    StoreOrder,
    StoreOrderItem,
)
from store.models import Category as PCategory
from user.models import Seller, Wishlist, ProductWishlist
from django.core.paginator import Paginator, EmptyPage
from django.db.models.query_utils import Q
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from django.contrib.auth.decorators import login_required
from .utils import cartData
from user.models import Address, TalentUser, OtherCountry
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from duniyadekhegi.settings import USE_S3, USER_STORE_IMG_PATH, USER_STORE_VID_PATH, USER_STORE_LOGO_PATH
from duniyadekhegi.storage_backends import PublicMediaStorage
from django.core.files.storage import FileSystemStorage

import razorpay
import json
import os
import shortuuid

rpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def store(request):
    data = cartData(request)
    products_list = RecommendedProduct.objects.all().order_by("rank").values_list("product", flat=True)
    products = [Product.objects.get(id=i) for i in products_list]
    products = filter(lambda product: product.added_by.is_kyc_done, products)
    context = {
        "recommended": products,
        "items": data["items"],
        "order": data["order"],
        "cartItems": data["cartItems"],
        "categories": data["categories"],
    }
    return render(request, "store/store.html", context)


def category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    cart_data = cartData(request)
    try:
        wishlistproducts = request.user.customer.wishlist_products
    except:
        wishlistproducts = None
    data = {
        "products": products,
        "cartItems": cart_data["cartItems"],
        "order": cart_data["order"],
        "items": cart_data["items"],
        "categories": cart_data["categories"],
        "wishlistproducts": wishlistproducts,
    }
    return render(request, "store/searchresults.html", data)


def search(request):
    keyword = request.POST.get("keyword").split("?")[0] if request.POST.get("keyword") else ''
    products_list = Product.objects.filter(
        Q(name__icontains=keyword)
        | Q(category__name__icontains=keyword)
        | Q(description__icontains=keyword)
        | Q(added_by__generaluser__name__icontains=keyword)
    ).order_by("-id")
    categories = set([product.category for product in products_list])
    cart_data = cartData(request)
    total_products = len(products_list)
    p = Paginator(products_list, 15)
    page_num = int(request.POST.get("page", 1))
    try:
        page = p.get_page(page_num)
    except EmptyPage:
        page = p.get_page(1)
        page_num = 1
    from_results = (page_num - 1) * 15 + 1
    to_results = min(page_num * 15, total_products)
    data = {
        "products": page,
        "categories": categories,
        "cartItems": cart_data["cartItems"],
        "order": cart_data["order"],
        "items": cart_data["items"],
        "categories": cart_data["categories"],
        "keyword": keyword,
        "from_results": from_results,
        "to_results": to_results,
        "total_products": total_products,
    }
    if request.user.is_authenticated:
        wishlist_items = ProductWishlist.objects.filter(wishlist_of=request.user).values_list("wishlist_product", flat=True)
        data['wishlistItems'] = wishlist_items
    return render(request, "store/searchresults.html", data)

def product_filter(request):
    if "category_search" in request.POST:
        price_search = request.POST.get("price_search")
        keyword = request.POST.get("keyword")
        category_search = request.POST.get("category_search")
        rating_search = request.POST.get("rating_search")

        if keyword:
            keyword = request.POST.get("keyword").split("?")[0] if request.POST.get("keyword") else ''
            products = Product.objects.filter(
                Q(name__icontains=keyword)
                | Q(category__name__icontains=keyword)
                | Q(description__icontains=keyword)
                | Q(added_by__generaluser__name__icontains=keyword)
            ).order_by("-id")
        else:
            products = Product.objects.all()

        categories = set([product.category for product in products])
        if category_search != "all":
            products = products.filter(category__name__icontains=category_search)
        if price_search:
            min_price_search, max_price_search = (i for i in price_search.split("-"))
            products = products.filter(Q(price__gte=min_price_search) & Q(price__lte=max_price_search))
        if rating_search:
            products = [p for p in products if p.rating >= int(rating_search)]

        data = {"products": products, "categories": categories}
        return render(request, "includes/searchproduct.html", data)


@login_required
def checkout(request):
    data = cartData(request)
    order_db = data["order"]
    if request.method == "POST":
        address_id = int(request.POST.get("address"))
        address = Address.objects.get(id=address_id)
        amount = int(data["order"].get_cart_total * 100)
        razorpay_order = rpay_client.order.create(dict(amount=amount, currency="INR", payment_capture="0"))
        razorpay_order_id = razorpay_order["id"]
        order_db.razorpay_order_id = razorpay_order_id
        order_db.address_line = address.address
        order_db.state = address.state.name
        order_db.city = address.city.name
        order_db.pincode = address.pincode
        order_db.amount = amount / 100
        order_db.save()
        return HttpResponse("success")
    else:
        razorpay_order_id = order_db.razorpay_order_id
        amount = order_db.amount
    context = {
        "items": data["items"],
        "order": order_db,
        "cartItems": data["cartItems"],
        "categories": data["categories"],
        "currency": "INR",
        "razorpay_order_id": razorpay_order_id,
        "razorpay_merchant_id": settings.RAZORPAY_KEY_ID,
        "razorpay_amount": amount,
    }
    return render(request, "store/checkout.html", context)


@csrf_exempt
def payment_handler(request):
    if request.method == "POST":
        # return HttpResponse(str(request.POST))
        try:
            razorpay_payment_id = request.POST.get("razorpay_payment_id", "")
            razorpay_order_id = request.POST.get("razorpay_order_id", "")
            razorpay_signature = request.POST.get("razorpay_signature", "")
            params_dict = {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }
            print(params_dict)
            try:
                order_db = StoreOrder.objects.get(razorpay_order_id=razorpay_order_id)
            except:
                return HttpResponse("505 Order not found")
            order_db.razorpay_payment_id = razorpay_payment_id
            order_db.razorpay_signature = razorpay_signature
            order_db.save()
            print("Starting to verify signature")
            try:
                result = rpay_client.utility.verify_payment_signature(params_dict)
            except Exception as e:
                print(e)
            print(str(result))
            if result is None:
                amount = int(order_db.get_cart_total * 100)
                try:
                    print("capturing payment")
                    print(amount)
                    rpay_client.payment.capture(razorpay_payment_id, amount)
                    print("payment captured")
                    order_db.payment_status = 1
                    order_db.is_complete = True
                    order_db.save()
                    return redirect("store")
                except:
                    order_db.payment_status = 2
                    order_db.save()
                    return redirect("store")
            else:
                order_db.payment_status = 2
                order_db.save()
                return redirect("store")
        except:
            return HttpResponse("505 bad request")


def add_to_wishlist(request):
    pid = request.POST.get("pid")
    product = Product.objects.get(id=pid)
    wishlist_item, _ = ProductWishlist.objects.get_or_create(wishlist_of=request.user, wishlist_product=product)
    if not _:
        wishlist_item.delete()
        return JsonResponse({"success": 1, "msg": "Product removed from wishlist"})
    return JsonResponse({"success": 1, "msg": "Product added to wishlist"})


def update_item(request):
    #FIXME: remove print statements
    data = json.loads(request.body)
    product_id = data['productId']
    print("type of product id",type(product_id))
    action = data['action']
    customer = request.user
    product = Product.objects.get(id=product_id)
    print("product",product)
    
    order, _ = StoreOrder.objects.get_or_create(user=customer, is_complete=False)
    print("order ",order)
    orderItem, _ = StoreOrderItem.objects.get_or_create(order=order, product=product)
    print("order-item",orderItem)
    if action == 'add':
        orderItem.quantity += 1
        orderItem.save()
    elif action == "remove":
        orderItem.quantity -= 1
        orderItem.save()
    elif action == "delete":
        orderItem.delete()

    if orderItem.quantity <= 0:
        orderItem.delete()
    print('success')    
    return JsonResponse('Item was addded.', safe=False)

def process_order(request):
    transaction_id = datetime.now().timestamp()

    if request.user.is_authenticated:
        customer = request.user
        address_id = int(request.POST.get("address"))
        address = Address.objects.get(id=address_id)
        order, _ = StoreOrder.objects.get_or_create(user=customer, is_complete=False)
        order.address = address
    else:
        customer, order = guestOrder(request)
    total = float(request.POST["total"])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.is_complete = True
        order.amount = total
    order.save()
    return JsonResponse("Payment Complete", safe=False)


@login_required
def profile(request):
    profile = Customer.objects.get(user=request.user)
    cart_data = cartData(request)
    orderlist = StoreOrder.objects.filter(customer=request.user.customer, complete=True).order_by("-date_ordered")
    orders_data = {}
    for order in orderlist:
        id = order.id
        orders_data[id] = {}
        orders_data[id]["order"] = order
        orders_data[id]["order_items"] = order.orderitem_set.all()
    addresses = Address.objects.filter(user=request.user.customer)
    data = {
        "profile": profile,
        "cartItems": cart_data["cartItems"],
        "order": cart_data["order"],
        "items": cart_data["items"],
        "orderslist": orderlist,
        "wishlistitems": request.user.customer.wishlist_products,
        "addresses": addresses,
    }
    if request.user.is_seller:
        products = Product.objects.filter(added_by=request.user.seller)
        data["added_products"] = products
        completed_orders = StoreOrder.objects.filter(complete=True).order_by("-date_ordered")
        received_orders = {}
        for order in completed_orders:
            items = order.orderitem_set.filter(product__in=products).values_list("product")
            items_products = Product.objects.filter(id__in=items)
            if items_products:
                received_orders[order.id] = {}
                received_orders[order.id]["order"] = order
                received_orders[order.id]["products"] = items_products
        data["received"] = received_orders
    return render(request, "store/userprofile.html", data)


def save_profile(request):
    profile = Customer.objects.get(user=request.user)
    name = request.POST.get("name")
    profile.name = name
    profile.save()
    return HttpResponse()


def add_address(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        address = request.POST["address"]
        city = request.POST["city"]
        state = request.POST["state"]
        pincode = request.POST["pincode"]

        addressObj = NewAddress.objects.create(
            name=name,
            email=email,
            pincode=pincode,
            addressline=address,
            city=city,
            state=state,
        )
        if request.user:
            customer = Customer.objects.get(user=request.user)
            addressObj.user = customer
            addressObj.save()
        return HttpResponse("")

@login_required
def manage_store(request):
    signin_user = request.user
    product_categories = PCategory.objects.values_list("name", flat=True)
    try:
        products = Product.objects.filter(added_by=request.user.seller)
    except:
        products = None
    data = {
        "product_categories": product_categories,
        "products": products,
    }
    # DELETE PRODUCT 
    if 'product_id' in request.POST:
        Product.objects.filter(id=request.POST['product_id']).delete()
        return JsonResponse({"success": 1})

    # CHECK STORE NAME 
    if "store_name" in request.GET:
        store_name = request.GET["store_name"]
        if not store_name:
            return JsonResponse({"error": "Error: store name cannot be empty"})
        else:
            store_name = Seller.objects.values_list("store_name", flat=True).exclude(pk=signin_user.seller.id)
            isStoreNameExist = False
            for name in store_name:
                if name == store_name:
                    isStoreNameExist = True
                    break
            if isStoreNameExist:
                return JsonResponse({"error": "Error: store name has been taken"})
            else:
                return JsonResponse({"success": 1})

    # SAVING STORE NAME AND DESCRIPTION
    if "store_desc" in request.POST:
        store_name = request.POST["store_name"]
        store_desc = request.POST["store_desc"]

        seller, _ = Seller.objects.get_or_create(generaluser=signin_user)
        seller.store_name = store_name
        seller.store_description = store_desc
        seller.save()

        return JsonResponse({"success": 1})

    # HANDLE STORE-LOGO
    try:
        if request.FILES.get("image"):
            seller, _ = Seller.objects.get_or_create(generaluser=signin_user)
            seller.store_logo.delete()

            img_obj = request.FILES.get("image", 0)
            img_name = signin_user.userlink + ".png"
            img_path = os.path.join(USER_STORE_LOGO_PATH, img_name)
            if USE_S3:
                fs = PublicMediaStorage()
                fs.save(img_path, img_obj)
            else:
                fs = FileSystemStorage(location=USER_STORE_LOGO_PATH)
                fs.save(img_name, img_obj)
            seller.store_logo = img_path
            seller.save()
            return JsonResponse({"success": 1})
    except Exception as e:
        print(e)
        return JsonResponse({"error": "Error: Something went wrong"})

    #DELETE STORE LOGO
    if request.method == "DELETE":
        signin_user.seller.store_logo.delete()
        return JsonResponse({"success": 1})

    return render(request, "store/manage-store.html", data)

def add_product(request):
    seller = request.user.seller

    name = request.POST.get("name")
    category_text = request.POST.get("category")
    price = float(request.POST.get("price"))
    description = request.POST.get("description").strip()
    category = Category.objects.get(name__iexact=category_text)

    try:
        db_product = Product.objects.get(name=name, added_by=seller)
    except:
        db_product = None
    
    # if product in database means it need to update 
    if db_product:
        Product.objects.filter(name=name, added_by=seller).update(category=category, price=price, description=description)
        product = get_object_or_404(Product, name=name, added_by=seller) 
        ProductImage.objects.filter(product=product).delete()
        ProductVideo.objects.filter(product=product).delete()
    else:
        product = Product.objects.create(
            name=name, added_by=seller, category=category, price=price, description=description
        )

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
            file_loc = os.path.join(USER_STORE_VID_PATH, request.user.userlink)
            file_path = os.path.join(file_loc, new_name)
            ProductVideo.objects.create(product=product, video=file_path)
        else:
            file_loc = os.path.join(USER_STORE_IMG_PATH, request.user.userlink)
            file_path = os.path.join(file_loc, new_name)
            ProductImage.objects.create(product=product, image=file_path)
        if USE_S3:
            fs = PublicMediaStorage()
            fs.save(file_path, file)
        else:
            fs = FileSystemStorage(location=file_loc)
            fs.save(new_name, file)
    if thumbnail_ext and thumbnail_ext.lower() in ["mp4", "mov", "avi", "webm"]:
        product.thumbnail = os.path.join(USER_STORE_VID_PATH, request.user.userlink, thumbnail)
    else:
        product.thumbnail = os.path.join(USER_STORE_IMG_PATH, request.user.userlink, thumbnail)
    product.save()
    if db_product:
        return JsonResponse({"success": 1, "msg": "Product edited successfully"}, status=200)
    else:
        return JsonResponse({"success": 1, "msg": "Product added successfully"}, status=202)


def delete_address(request):
    id = request.POST.get("id")
    try:
        address = Address.objects.get(id=id).delete()
    except:
        pass
    return HttpResponse()


def get_product_data(request):
    id = request.GET.get("id")
    product = Product.objects.get(id=id)
    return JsonResponse(
        {"name": product.name, "price": int(product.price), "url": product.image.url, "category": product.category.name}
    )


def submit_review(request):
    pid = int(request.POST.get("pid"))
    title = request.POST.get("title")
    description = request.POST.get("description")
    stars = request.POST.get("stars")
    product = Product.objects.get(id=pid)

    Review.objects.create(
        customer=request.user.customer, product=product, rating=stars, title=title, detail=description
    )
    return HttpResponse()


def filter_results(request):
    minrange = request.GET.get("minrange")
    maxrange = request.GET.get("maxrange")
    keyword = request.GET.get("keyword")

    products_list = Product.objects.filter(
        Q(name__icontains=keyword)
        | Q(category__name__icontains=keyword)
        | Q(description__icontains=keyword)
        | Q(added_by__name__icontains=keyword)
    )
    if minrange:
        products_list = products_list.filter(price__gte=int(minrange))
    if maxrange:
        products_list = products_list.filter(price__lte=int(maxrange))
    cart_data = cartData(request)
    categories = set([product.category for product in products_list])
    products_list = list(products_list)
    data = {
        "products": products_list,
        "categories": categories,
        "cartItems": cart_data["cartItems"],
        "order": cart_data["order"],
        "items": cart_data["items"],
    }
    if request.user.is_authenticated:
        data["wishlistproducts"] = request.user.customer.wishlist_products
    return render(request, "store/searchresults.html", data)


def product_detail(request, slug):
    product = Product.objects.get(slug=slug)
    product_images = ProductImage.objects.filter(product=product)
    product_videos = ProductVideo.objects.filter(product=product) 
    reviews = Review.objects.filter(product=product)
    
    review_chart_data = {
        5: [0, 0],
        4: [0, 0],
        3: [0, 0],
        2: [0, 0],
        1: [0, 0],
    }  # 1st element is percent and second is count.
    review_count = len(reviews)
    for review in reviews:
        n = review.rating
        review_chart_data[n][0] += 1
        review_chart_data[n][1] += 1
    if review_count:
        for k, v in review_chart_data.items():
            review_chart_data[k][0] = 100 * (v[0] / review_count)
    cart_data = cartData(request)
    data = {
        "product": product,
        "product_images": product_images,
        "product_videos": product_videos,
        "review_count": review_count,
        "review_chart_data": review_chart_data,
        "reviews": reviews,
        "cartItems": cart_data["cartItems"],
        "order": cart_data["order"],
        "items": cart_data["items"],
    }
    if request.user.is_authenticated:
        wishlist_items = ProductWishlist.objects.filter(wishlist_of=request.user).values_list("wishlist_product", flat=True)
        data['wishlistItems'] = wishlist_items
    return render(request, "store/productdetails.html", data)


def personal_store(request, id):
    seller = Seller.objects.get(id=id)
    if request.user.is_authenticated and hasattr(request.user, "seller"):
        if request.user.seller != seller and not seller.is_kyc_done:
            return redirect('home')
    else:
        if not seller.is_kyc_done:
            return redirect('home')

    cart_data = cartData(request)
    products = Product.objects.filter(added_by=seller)
    data = {}
    data = {
        "products": products,
        "cartItems": cart_data["cartItems"],
        "order": cart_data["order"],
        "items": cart_data["items"],
        "categories": cart_data["categories"],
        "seller": seller,
    }
    if request.user.is_authenticated:
        wishlist_items = ProductWishlist.objects.filter(wishlist_of=request.user).values_list("wishlist_product", flat=True)
        data['wishlistItems'] = wishlist_items
    return render(request, "store/personalstore.html", data)

def productwishlist(request):
    wishlistproducts = request.user.wishlist_products 
    wishlist_profiles = Wishlist.objects.filter(wishlist_of=request.user)
    data={
        'wishlistproducts': wishlistproducts,
        'wishlist_profiles': wishlist_profiles
    }
    return render(request,'store/productwishlist.html',data)
