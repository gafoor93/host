from django.contrib import admin
from django.urls import path
from.import views


urlpatterns = [
    path('',views.index,name="index"),
    path('Login',views.user_login,name="user_login"),
    path('Register',views.user_register,name="user_register"),
    path('user_logout',views.user_logout,name="user_logout"),
    path('Add_Product',views.Add_Product,name="add_product"),
    path('product_desc/<pk>',views.product_desc,name="product_desc"),
    path("add_to_cart/<pk>",views.add_to_cart,name="add_to_cart"),
    path("orderlist",views.orderlist,name='orderlist'),
    path("add_item/<int:pk>",views.add_item,name="add_item"),
    path('remove_item/<int:pk>',views.remove_item,name="remove_item"),
    path('checkout',views.checkout,name='checkout'),
    path('payment',views.payment,name='payment'),
    path('handlerequest',views.handlerequest,name='handlerequest'),
    path('contact',views.contact,name='contact'),
    path('contactinfo',views.contactinfo,name='contactinfo'),
]
