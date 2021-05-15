from django.urls import path
from feshion import views
from .views import Index, Signup, Login, logout, Cart, Checkout, OrderView, contact,store,Order_place,shop,search,myaccount
from .middlewares.auth import  auth_middleware


urlpatterns = [
    path('',Index.as_view(),name='index'),
    path('signup',Signup.as_view(),name='signup'),
    path('login',Login.as_view(),name='login'),
    path('logout',logout,name='logout'),
#    path('cart/', auth_middleware(Cart.as_view()) , name='cart'),
    path('cart', Cart.as_view(), name='cart'),
    path('checkout',Checkout.as_view(),name='checkout'),
    path('order_place',Order_place.as_view(),name='order_place'),
#    path('order/', auth_middleware(OrderView.as_view()), name='order'),
    path('order', OrderView.as_view(), name='order'),
    path('store',store, name='store'),
    path('contact',contact,name='contact'),
    path('shop/',shop,name='shop'),
    path('search',search,name='search'),
    path('complete',views.paymentComplete,name='complete'),
    path('myaccount',myaccount,name='myaccount'),


]
