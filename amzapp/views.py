from django.shortcuts import render, redirect
from .models import Product, Contact, OrderUpdate, Orders
from django.contrib import messages
from math import ceil
import razorpay
from django.conf import settings
from django.core.mail import send_mail
from django.template import RequestContext

# Create your views here.


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


def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/accounts/login')

    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amt')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2','')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        print('basic code completed')
        
        # thank = True
        print('************client called*****************')
        client= razorpay.Client(auth=(settings.KEY, settings.SECRET))
        print('**************creating payment********************')
        payment= client.order.create({'amount': amount*100, 'currency': 'INR', 'payment_capture' : 1})
        print('payment created')
        Order = Orders(items_json=items_json,name=name,amount=int(amount)*100, email=email, address1=address1,address2=address2,city=city,state=state,zip_code=zip_code,phone=phone, razor_pay_order_id= payment['id'])
        print(type(amount))
        Order.save()
        update = OrderUpdate(order_id=Order.order_id,update_desc="the order has been placed")
        update.save()
        print('*************************************')
        print(payment)
        print('*************************************')
        print(type(payment['amount']))
        context= {"payment" : payment}
        print('passing context')
        messages.success(request, 'your payment added successfully order will be delivered soon go to home:)', payment['id'])
        # return render(request, 'checkout.html', context)
        # return redirect('/')
        return render('index.html', RequestContext(request))

        
    return render(request, 'checkout.html')

    