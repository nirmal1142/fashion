from django.contrib import admin
from .models import Category, Product, Customer,Order
# Register your models here.


class AdminProduct(admin.ModelAdmin):
    list_display = ['name','price','category']


class AdminCategoty(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Product,AdminProduct)
admin.site.register(Category,AdminCategoty)
admin.site.register(Customer)
admin.site.register(Order)