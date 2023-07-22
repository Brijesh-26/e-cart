from django.shortcuts import render, redirect
from .models import Product, Contact, OrderUpdate, Orders
from django.contrib import messages
from math import ceil
import razorpay
from django.conf import settings
from django.core.mail import send_mail
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect , csrf_exempt
from django.http import HttpResponseBadRequest

# Create your views here.

@csrf_exempt
def index(request):
    allProds = []
    catprods = Product.objects.values('category','id')
    print(catprods)
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod= Product.objects.filter(category=cat)
        n=len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    params= {'allProds':allProds}

    return render(request,"index.html",params)

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method=="POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        desc=request.POST.get("desc")
        pnumber=request.POST.get("pnumber")
        myquery=Contact(name=name,email=email,desc=desc,phonenumber=pnumber)
        myquery.save()
        
        send_mail(
            name+"->"+pnumber,
            desc,
            email,
            ["djangowork97@gmail.com"],
            fail_silently=False,
        )
        
        messages.success(request,"we will get back to you soon..")
        return redirect('/')


    return render(request,"contact.html")



def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/auth/login')
    currentuser=request.user.username
    items=Orders.objects.filter(name=currentuser)
    rid=""
    for i in items:
        print(i.oid)
        # print(i.order_id)
        myid=i.oid
        rid=myid.replace("ShopyCart","")
        print(rid)
    status=OrderUpdate.objects.filter(order_id=int(rid))
    for j in status:
        print(j.update_desc)

   
    context ={"items":items,"status":status}
    # print(currentuser)
    return render(request,"profile.html",context)



razorpay_client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/accounts/login')
    
    else : 
        currency = 'INR'
        amount = 20000  # Rs. 200
    
        # Create a Razorpay Order
        razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                        currency=currency,
                                                        payment_capture='0'))
    
        # order id of newly created order.
        razorpay_order_id = razorpay_order['id']
        # callback_url = 'paymenthandler/'
        callback_url = '/paymenthandler/'
    
        # we need to pass these details to frontend.
        context = {}
        context['razorpay_order_id'] = razorpay_order_id
        context['razorpay_merchant_key'] = settings.KEY
        context['razorpay_amount'] = amount
        context['currency'] = currency
        context['callback_url'] = callback_url
    
        return render(request, 'checkout.html', context=context)
    
    
    
    
@csrf_exempt
def paymenthandler(request):
 
    # only accept POST request.
    if request.method == "POST":
        try:
           
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
 
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is not None:
                amount = 20000  # Rs. 200
                try:
 
                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)
 
                    # render success page on successful caputre of payment
                    messages.success(request,"You will recieve your orders soon")
                    return render(request, 'paymentsuccess.html')
                except:
 
                    # if there is an error while capturing payment.
                    messages.danger(request,"Check Your Internet Connection")
                    return render(request, 'paymentfail.html')
            else:
 
                # if signature verification fails.
                messages.danger(request,"Check Your Internet Connection")
                return render(request, 'paymentfail.html')
        except:
 
            # if we don't find the required parameters in POST data
            # return HttpResponseBadRequest()
            return render(request, 'wrong.html')
    else:
       # if other than POST request is made.
        return render(request, 'wrong1.html')