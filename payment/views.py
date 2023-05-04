from django.http.response import HttpResponseBadRequest
from django.shortcuts import render

import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))

def home(request):
    currecny = 'INR'
    amount = 15000
    razorpay_order = client.order.create(dict(amount=amount,currency=currecny,payment_capture='1',receipt='#ABCDEFG'))
    razorpay_order_id = razorpay_order['id']
    callback_url = 'paymenthandler/'
    context = {
        'razorpay_order_id':razorpay_order_id,
        'razorpay_merchant_id':settings.RAZORPAY_KEY_ID,
        'razorpay_amount':amount,
        'currency':currecny,
        'callback_url':callback_url
    }
    return render(request,'payment/index.html',context)

@csrf_exempt
def paymenthandler(request):
    if request.method == 'POST':
        try:
            payment_id = request.POST.get('razorpay_payment_id','')
            razorpay_order_id = request.POST.get('razorpay_order_id','')
            signature = request.POST.get('razorpay_signature','')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            result = client.utility.verify_payment_signature(params_dict)
            if result is None:
                amount = 15000
                try:
                    # capture payment 
                    client.payment.capture(payment_id,amount)
                    
                    # render success page
                    return render(request,'payment/success.html')
                except:
                    
                    return render(request,'payment/failed.html')
            else:
                return render(request,'payment/failed.html')
        except:
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()