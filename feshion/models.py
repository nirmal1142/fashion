import datetime

from django.contrib.auth.models import User
from django.db import models

# Create your models here.




class Category(models.Model):
    name=models.CharField(max_length=20)


    @staticmethod
    def get_all_categories():
        return Category.objects.all()

    def __str__(self):
        return self.name



class Product(models.Model):
    name=models.CharField(max_length=50)
    price=models.IntegerField(default='0')
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    discription=models.CharField(max_length=300,default='',blank=True,null=True)
    image=models.ImageField(upload_to='upload/product')
    date_added = models.DateTimeField(auto_now_add=True)
    num_available = models.IntegerField(default=1)
    num_visits = models.IntegerField(default=0)
    last_visit = models.DateTimeField(blank=True, null=True)


    @staticmethod
    def get_products_by_id(ids):
        return Product.objects.filter(id__in=ids)


    @staticmethod
    def get_all_products():
        return Product.objects.all()



    @staticmethod
    def get_all_products_by_categoryid(category_id):
        if category_id:
            return Product.objects.filter(category=category_id)
        else:
            return Product.get_all_products();




class Customer(models.Model):
    first_name=models.CharField(User,max_length=50)
    last_name=models.CharField(max_length=50)
    phone=models.CharField(max_length=15)
    email=models.EmailField()
    password=models.CharField(max_length=500)

    User.userprofile = property(lambda u:Customer.objects.get_or_create(user=u)[0])


    def register(self):
        self.save()


    @staticmethod
    def get_customer_by_email(email):
        try:
            return Customer.objects.get(email=email)
        except:
            return False


    def isExists(self):
        if Customer.objects.filter(email=self.email):
            return True
        return False





class Order(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    customer=models.ForeignKey(Customer,on_delete=models.CASCADE)
    quantity=models.IntegerField(default=1)
    price=models.IntegerField()
    firstname=models.CharField(max_length=15)
    lastname=models.CharField(max_length=10)
    country=models.CharField(max_length=10)
    address=models.CharField(max_length=500)
    city=models.CharField(max_length=15)
    state=models.CharField(max_length=15)
    phone=models.CharField(max_length=15)
    email=models.EmailField(max_length=50)
    postcode=models.IntegerField()
    date=models.DateField(default=datetime.datetime.today)
    ordered=models.BooleanField(default=False)

    def __str__(self):
        return self.product.name


    def placeOrder(self):
        self.save()

    @staticmethod
    def get_orders_by_customer(customer_id):
        return Order.objects.filter(customer=customer_id).order_by('-date')