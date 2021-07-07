from django import http
from django.http import response
from django.shortcuts import render
from django.http import HttpResponse
from .models import Product, Contact, Order, OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from PayTm import PaytmChecksum
MERCHANT_KEY = 'kbzk1DSbJiV_O3p5'

# Create your views here.
def index(request):
    # product=Product.objects.all()
    # n=len(product)
    # nSlides= n//4 + ceil((n/4)-(n//4))
    # params={'product':products, 'no_slides':nSlides, 'range':range(1,nSlides)}
    # allProds=[[product, range(1, nSlides), nSlides],
    #             [product, range(1, nSlides), nSlides]]
    allProds=[]
    catprods=Product.objects.values('category', 'id', 'price')
    cats={item['category'] for item in catprods}
    for cat in cats:
        prod=Product.objects.filter(category=cat)
        n=len(prod)
        nSlides= n//4 + ceil((n/4)-(n//4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params={'allProds':allProds}
    return render(request, 'shop/index.html', params)

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    sent = False
    if(request.method == 'POST'):
        name=request.POST.get('name', '')
        email=request.POST.get('email', '')
        phone=request.POST.get('phone', '')
        desc=request.POST.get('contactdesc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        sent = True
    return render(request, 'shop/contact.html', {'sent': sent})

def tracker(request):
    if request.method == 'POST':
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        # return HttpResponse(f"{orderId} and {email}")
        try:
            order = Order.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates=[]
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({'status':'success', 'updates': updates, 'itemsJSON': order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status": "noitem"}')
        except Exception as e:
            return HttpResponse('{"status": "error"}')
    return render(request, 'shop/tracker.html')

def searchMatch(query, item):
    '''return true only if query matches the item'''
    query = query.lower()
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds=[]
    catprods=Product.objects.values('category', 'id', 'price')
    cats={item['category'] for item in catprods}
    for cat in cats:
        prodtemp=Product.objects.filter(category=cat)
        prod=[item for item in prodtemp if searchMatch(query, item)]
        n=len(prod)
        nSlides= n//4 + ceil((n/4)-(n//4))
        if n!=0:
            allProds.append([prod, range(1, nSlides), nSlides])
    msg=""
    params={'allProds':allProds, 'msg': msg}
    print(len(msg))
    if len(allProds) == 0 or len(query)<3:
        params = {'msg': "Please enter relevant query"}
    
    return render(request, 'shop/search.html', params)

def productView(request, myid):
    #fetch the products using id
    product=Product.objects.all()
    print(product)
    return render(request, 'shop/prodview.html', {'product':product[myid-1]})

def checkout(request):
    if(request.method == 'POST'):
        items_json = request.POST.get('itemsJSON', '')
        amount = request.POST.get('amount', '')
        name=request.POST.get('name', '')
        email=request.POST.get('email', '')
        phone=request.POST.get('phone')
        address=request.POST.get('address1', '')+" "+request.POST.get('address2', '')
        city=request.POST.get('city', '')
        state=request.POST.get('state', '')
        zip_code=request.POST.get('zip_code', '')
        order = Order(name=name, email=email, phone=phone, address=address, city=city, state=state, zip_code=zip_code, items_json=items_json, amount=amount)
        order.save()
        thank = True
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed :)")
        update.save()
        id=order.order_id
        # return render(request, 'shop/checkout.html', {'thank':thank, 'id':id})
        # request paytm to take the payment
        param_dict={
            'MID':'WorldP64425807474247',
            'ORDER_ID': str(order.order_id),
            'TXN_AMOUNT': str(amount),
            'CUST_ID':email,
            'INDUSTRY_TYPE_ID':'Retail',
            'WEBSITE':'WEBSTAGING',
            'CHANNEL_ID':'WEB',
	        'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/',
        }
        param_dict['CHECKSUMHASH'] = PaytmChecksum.generateSignature(param_dict, MERCHANT_KEY)
        return render(request, 'shop/paytm.html', {'param_dict':param_dict, 'order':order})
    return render(request, 'shop/checkout.html')

@csrf_exempt
def handleRequest(request):
    # paytm will send post request here
    form = request.POST
    response_dict = {}
    for i in form.key():
        response_dict[i]=form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]
    verify = PaytmChecksum.verifySignature(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE']=='01':
            print('order successful')
        else:
            print('order not successful because '+response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})
    pass