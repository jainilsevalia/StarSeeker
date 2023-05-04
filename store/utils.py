import json
from .models import *

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}
    items = []
    order = {'get_cart_total':0, 'get_cart_items':0}
    cartItems = order['get_cart_items']
    
    for i in cart:
        try:
            # cartItems += cart[i]['quantity']
            cartItems += 1
            
            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])
            
            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']
            
            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.image.url,
                },
                'quantity': cart[i]['quantity'],
                'get_total': total,
            }
            items.append(item)
        except:
            pass
    
    return {'cartItems': cartItems, 'order': order, 'items': items}

def cartData(request):
    categories = Category.objects.all()
    if request.user.is_authenticated:
        customer =request.user
        order, _ = StoreOrder.objects.get_or_create(user=customer, is_complete=False)
        items = order.cartitem.all()
        cartItems = order.get_cart_items_count
    else:
        # cookieData = cookieCart(request)
        # cartItems = cookieData['cartItems']
        # order = cookieData['order']
        # items = cookieData['items']
        items = None
        order = None
        cartItems = 0
    return {'cartItems': cartItems, 'order': order, 'items': items, 'categories': categories}

