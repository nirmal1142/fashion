import json
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from paypal.standard.forms import PayPalPaymentsForm

from .models import Product, Category, Customer, Order


# Create your views here.


class Index(View):

    def post(self, request):
        product = request.POST.get('product')
        remove = request.POST.get('remove')
        cart = request.session.get('cart')
        if cart:
            quantity = cart.get(product)
            if quantity:
                if remove:
                    if quantity <= 1:
                        cart.pop(product)
                    else:
                        cart[product] = quantity - 1
                else:
                    cart[product] = quantity + 1

            else:
                cart[product] = 1
        else:
            cart = {}
            cart[product] = 1

        request.session['cart'] = cart
        print('cart', request.session['cart'])
        return redirect('shop')

    def get(self, request):
        # print()
        return HttpResponseRedirect(f'/store{request.get_full_path()[1:]}')


def store(request):
    cart = request.session.get('cart')
    if not cart:
        request.session['cart'] = {}
    products = None
    categories = Category.get_all_categories()
    categoryID = request.GET.get('category')
    if categoryID:
        products = Product.get_all_products_by_categoryid(categoryID)
    else:
        products = Product.get_all_products()

    data = {}
    data['products'] = products
    data['categories'] = categories

    print('you are : ', request.session.get('email'))
    return render(request, 'index.html', data)



def shop(request):
    recently_viewed_products = Product.objects.all().order_by('-last_visit')[0:4]
    cart = request.session.get('cart')
    if not cart:
        request.session['cart'] = {}
    products = None
    categories = Category.get_all_categories()
    categoryID = request.GET.get('category')
    if categoryID:
        products = Product.get_all_products_by_categoryid(categoryID)
    else:
        products = Product.get_all_products()

    data = {}
    data['products'] = products
    data['categories'] = categories

    print('you are : ', request.session.get('email'))
    return render(request, 'shop.html', data)
#    return render(request,'shop.html')





def search(request):

    query = request.GET.get('query')
    instock = request.GET.get('instock')
    price_from = request.GET.get('price_from', 0)
    price_to = request.GET.get('price_to', 100000)
    sorting = request.GET.get('sorting', '-date_added')
    products = Product.objects.filter(price__gte=price_from).filter(price__lte=price_to)

    if instock:
        products = products.filter(num_available__gte=1)

    context = {
        'query': query,
        'products': products.order_by(sorting),
        'instock': instock,
        'price_from': price_from,
        'price_to': price_to,
        'sorting': sorting
    }

    return render(request, 'shop.html', context)







class Signup(View):
    def get(self, request):
        return render(request, 'signup.html')

    def post(self, request):
        postData = request.POST
        first_name = postData.get('firstname')
        last_name = postData.get('lastname')
        phone = postData.get('phone')
        email = postData.get('email')
        password = postData.get('password')
        # validation
        value = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'email': email
        }
        error_message = None

        customer = Customer(first_name=first_name,
                            last_name=last_name,
                            phone=phone,
                            email=email,
                            password=password)
        error_message = self.validateCustomer(customer)

        if not error_message:
            print(first_name, last_name, phone, email, password)
            customer.password = make_password(customer.password)
            customer.register()
            return redirect('index')
        else:
            data = {
                'error': error_message,
                'values': value
            }
            return render(request, 'signup.html', data)

    def validateCustomer(self, customer):
        error_message = None
        if (not customer.first_name):
            error_message = "First Name Required !!"
        elif len(customer.first_name) < 4:
            error_message = 'First Name must be 4 char long or more'
        elif not customer.last_name:
            error_message = 'Last Name Required'
        elif len(customer.last_name) < 4:
            error_message = 'Last Name must be 4 char long or more'
        elif not customer.phone:
            error_message = 'Phone Number required'
        elif len(customer.phone) < 10:
            error_message = 'Phone Number must be 10 char Long'
        elif len(customer.password) < 6:
            error_message = 'Password must be 6 char long'
        elif len(customer.email) < 5:
            error_message = 'Email must be 5 char long'
        elif customer.isExists():
            error_message = 'Email Address Already Registered..'
        # saving

        return error_message




class Login(View):
    return_url = None
    def get(self , request):
        Login.return_url = request.GET.get('return_url')
        return render(request , 'login.html')

    def post(self , request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Customer.get_customer_by_email(email)
        error_message = None
        if customer:
            flag = check_password(password, customer.password)
            if flag:
                request.session['customer'] = customer.id

                if Login.return_url:
                    return HttpResponseRedirect(Login.return_url)
                else:
                    Login.return_url = None
                    return redirect('index')
            else:
                error_message = 'Email or Password invalid !!'
        else:
            error_message = 'Email or Password invalid !!'

        print(email, password)
        return render(request, 'login.html', {'error': error_message})

def logout(request):
    request.session.clear()
    return redirect('login')



class Cart(View):
    def get(self,request):
        ids=list(request.session.get('cart').keys())
        products=Product.get_products_by_id(ids)
        return render(request,'cart.html',{'products':products})



class Checkout(View):
    def post(self,request):
        address= request.POST.get('address')
        phone=request.POST.get('phone')
        firstname=request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        country=request.POST.get('country')
        city=request.POST.get('city')
        state=request.POST.get('state')
        postcode=request.POST.get('postcode')
        email=request.POST.get('email')
        customer=request.session.get('customer')
        cart=request.session.get('cart')
        products=Product.get_products_by_id(list(cart.keys()))


        for product in products:
            order = Order(customer=Customer(id=customer),
                          product=product,
                          price=product.price,
                          firstname=firstname,
                          lastname=lastname,
                          country=country,
                          city=city,
                          state=state,
                          postcode=postcode,
                          email=email,
                          address=address,
                          phone=phone,
                          quantity=cart.get(str(product.id)))

            order.save()
#            return redirect('process_payment')
        request.session['cart'] = {}
        return redirect('order')

class Order_place(View):
    def get(self,request):
        ids=list(request.session.get('cart').keys())
        products=Product.get_products_by_id(ids)
        return render(request,'checkout.html',{'products':products})





class OrderView(View):
    def get(self, request):
        customer=request.session.get('customer')
        orders=Order.get_orders_by_customer(customer)
#       orders=orders.reverse
 #       return redirect('process_payment')
        return render(request, 'order.html',{'orders':orders})



def contact(request):
    return render(request,'contact.html')




def paymentComplete(request):
    body=json.load(request.body)
    print('BODY:',body)
    product = Product.objects.get(id=body['productId'])
    Order.objects.create(
        product=product
    )

    return JsonResponse('paymentComplete',safe=False)


def myaccount(request):
    return render(request,'myaccount.html')







