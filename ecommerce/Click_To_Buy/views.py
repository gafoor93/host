from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render,redirect
from django.http import HttpResponse
from.models import *
from.forms import productform
from.forms import CheckoutForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.conf import settings
import razorpay
from django.views.decorators.csrf import csrf_exempt

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_ID, settings.RAZORPAY_SECRET))

# Create your views here.

def index(request):
    products = product.objects.all()
    return render(request,'home.html',{'products':products})

def contact(request):
    return render(request,'contact.html')

def contactinfo(request):
    return render(request,'contactinfo.html')

def orderlist(request):
    if Order.objects.filter(user=request.user,ordered=False).exists():
        order = Order.objects.get(user=request.user,ordered=False)
        return render(request,'orderlist.html',{'order':order})
    return render(request,'orderlist.html',{'message':"Your Cart is Empty" })


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password =  request.POST.get('password')
        user = authenticate(username = username, password = password)
        if user is not None:
            login(request,user)
            return redirect('/')
        messages.info(request,'username and password didn"t match')
    return render(request,'login.html')

def user_register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.info(request,'Username Is Already Exsits')


            else:
                if User.objects.filter(email=email).exists():
                    messages.info(request,'Email Already Exsits')



                else:
                    user = User.objects.create_user(username=username,email=email,password=password)
                    user.save()
                    data = costumer(user=user,phone_number=phone_number)
                    data.save()

                    # code for login of user will come here

                    our_user = authenticate(username=username,password=password)
                    if our_user is not None:
                        login(request,user)
                        return redirect('/')

        messages.info(request,'password didn"t match')

    return render(request,'register.html')

def user_logout(request):
    logout(request)
    return redirect('/')


def Add_Product(request):
    if request.method == "POST":
        form = productform(request.POST,request.FILES)
        if form.is_valid():
            print('True')
            form.save()
            print('Data Added Successfully')
            return redirect('/')
        else:
            print('Not working')
            messages.info('Product is Not Added')
    else:
        form = productform()
    return render(request,'add_product.html',{'form':form})


def product_desc(request,pk):
    products = product.objects.get(pk=pk)
    return render(request,'product_desc.html',{'product':products})



def add_to_cart(request, pk,):
    Product = product.objects.get(pk=pk)

    #create order item
    order_item, created = OrderItem.objects.get_or_create(
        Product = Product,
        user = request.user,
        ordered = False,
    )

    #Get query set order object of particular user
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(Product__pk = pk).exists():
            order_item.quantity +=1
            order_item.save()
            messages.info(request,"Item Added to Cart")
            return redirect('product_desc',pk=pk)
        else:
            order.items.add(order_item)
            messages.info(request,"Item Added to Cart")
            return redirect("product_desc",pk=pk)

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user,ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request,"Item Added to Cart")
        return redirect('product_desc',pk=pk)

def add_item(request,pk):
    Product = product.objects.get(pk=pk)

    # create order item
    order_item, created = OrderItem.objects.get_or_create(
        Product=Product,
        user=request.user,
        ordered=False,
    )

    # Get query set order object of particular user
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(Product__pk=pk).exists():
            if order_item.quantity < Product.product_available:
                order_item.quantity +=1
                order_item.save()
                messages.info(request, "Item Added to Cart")
                return redirect('orderlist')
            else:
                messages.info(request,"Sorry! Product is Out Stock")
                return redirect('orderlist')
        else:
            order.items.add(order_item)
            messages.info(request, "Item Added to Cart")
            return redirect("product_desc", pk=pk)

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Item Added to Cart")
        return redirect('product_desc', pk=pk)


def remove_item(request,pk):
    item = get_object_or_404(product,pk=pk)
    order_qs = Order.objects.filter(
        user = request.user,
        ordered = False,
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(Product__pk=pk).exists():
            order_item = OrderItem.objects.filter(
                Product = item,
                user = request.user,
                ordered =False,
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order_item.delete()
            messages.info(request,'Item Removed From Cart')
            return redirect('orderlist')
        else:
            messages.info(request,'This Item is Not in Your Cart')
            return redirect('orderlist')
    else:
        messages.info(request,'You Do not have Any Order')
        return redirect('orderlist')


def checkout(request):
    if CheckoutAddress.objects.filter(user=request.user).exists():
        return render(request,'checkout_address.html',{'payment_allow':"allow"})
    if request.method == 'POST':
        print('saving must start')
        form = CheckoutForm(request.POST)
        if form.is_valid():
            street_address = form.cleaned_data.get('street_address')
            apartment_address = form.cleaned_data.get('apartment_address')
            country = form.cleaned_data.get('country')
            zip_code = form.cleaned_data.get('zip_code')

            checkout_address = CheckoutAddress(
                user = request.user,
                street_address = street_address,
                apartment_address = apartment_address,
                country = country,
                zip_code = zip_code,
            )
            checkout_address.save()
            print("It Should Render in the Summary Page")
            return render(request,'checkout_address.html',{"payment_allow":'allow'})
        else:
            messages.warning(request,"Failed Checkout")
            return redirect('checkout')
    else:
        form = CheckoutForm()
        return render(request,'checkout_address.html',{'form':form})


def payment(request):
    try:
        order = Order.objects.get(user=request.user,ordered = False)
        address = CheckoutAddress.objects.get(user=request.user)
        order_amount = order.get_total_price()
        order_currency = "INR"
        order_receipt = order.order_id
        notes = {
            "street_address":address.street_address,
            "apartment_address":address.apartment_address,
            "country":address.country.name,
            "zip_code":address.zip_code,
        }
        razorpay_order = razorpay_client.order.create(
            dict(
                amount=order_amount * 100,
                currency = order_currency,
                receipt = order_receipt,
                notes = notes,
                payment_capture = "0",
            )
        )
        print(razorpay_order["id"])
        order.razorpay_order_id = razorpay_order["id"]
        order.save()
        print('It Should Render the Summary Page')
        return render(
            request,
            'paymentsummary.html',
            {
                "order":order,
                "order_id":razorpay_order['id'],
                "orderId":order.order_id,
                "final _price":order_amount,
                "razorpay_merchant_id":settings.RAZORPAY_ID,
            },
        )

    except Order.DoesNotExist:
        print("Order Not Found")
        return HttpResponse("404 Error")

@csrf_exempt
def handlerequest(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', "")
            order_id = request.POST.get('razorpay_order_id', "")
            signature = request.POST.get('razorpay_signature', "")
            print(payment_id, order_id, signature)
            params_dict = {
                "razorpay_order_id":order_id,
                "razorpay_payment_id": payment_id,
                "razorpay_signature": signature,
            }
            try:
                order_db = Order.objects.get(razorpay_order_id=order_id)
                print("order found")
            except:
                print('order not found')
                return HttpResponse('505 Not Found')
            order_db.razorpay_payment_id = payment_id
            order_db.razorpay_signature = signature
            order_db.save()
            print("Working.....")
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result == None:
                print("Working Final Fine")
                amount = order_db.get_total_price()
                amount=amount * 100
                payment_status = razorpay_client.payment.capture(payment_id, amount)
                if payment_status is not None:
                    print("payment status")
                    order_db.ordered = True
                    order_db.save()
                    print("payment success")
                    request.session[
                        "order complete"
                    ] = "Your Order Succeesfully Placed, You will Recieve Your Orden Within 6-7 Days"
                    return  render(request,'contact.html')
                else:
                    print("Payment Failed")
                    order_db.ordered = False
                    order_db.save()
                    request.session[
                        "Order Failed"
                    ] = "unfortunately Your Ordr Could Not Be Place, Try Again!"
                    return redirect("/")
            else:
                order_db.ordered =  False
                order_db.save()
                return render(request,"paymentfailed.html")
        except:
            return HttpResponse("Error Occured")




