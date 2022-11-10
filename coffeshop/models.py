from pydoc import describe
from random import choices
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
from django.utils.safestring import mark_safe # new
from PIL import Image as Im # new
from django.utils.text import slugify

IS_AVAILABLE = (
    ('true' , 'True'),
    ('false' , 'False'),
)


# Create your models here.
class User(AbstractUser, models.Model):
    email = models.EmailField(unique = True)
    date_of_birth = models.DateField(default = datetime.now)
    number_of_orders = models.IntegerField(default = 0)
    phone_number = models.CharField(max_length = 10, blank = True)

class Ingredient(models.Model):
    is_activated = models.CharField(max_length=10, choices=IS_AVAILABLE, default='true')
    ingredient_slug = models.SlugField(unique = True, max_length = 100, blank = True)
    name = models.CharField(max_length = 30)
    ingredient_price = models.DecimalField(default = 10, decimal_places = 3, max_digits = 5)
    is_optional = models.CharField(max_length=10,   choices = IS_AVAILABLE, default='true') 
    quantity = models.BigIntegerField(default = 0)
    description = models.TextField(max_length = 1000, default = "Ingredient description here!")
    ingredient_image = models.ImageField(null=True, blank=True, upload_to="images/")

    def image_tag(self): # new
        return mark_safe('<img src="/../../media/%s" width="150" height="150" />' % (self.ingredient_image))
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        
    def save(self, *args, **kwargs): # new
        super().save()
        super(Ingredient, self).save(*args, **kwargs)
        if self.ingredient_image:
            img = Im.open(self.ingredient_image.path)
            # resize it
            if img.height > 300 or img.width > 300:
                output_size = (300,300)
                img.thumbnail(output_size)
                img.save(self.ingredient_image.path)


class Order(models.Model):
    slug = models.SlugField(unique = True, max_length = 100, blank = True)
    name = models.CharField(default = "", max_length = 50)
    order_price = models.DecimalField(default = 10, decimal_places = 3, max_digits = 5)
    description = models.TextField(max_length = 1000, default = "Order description here!")
    order_ingredients = models.ManyToManyField(Ingredient, related_name = "order_ingredients")
    order_image = models.ImageField(null=True, blank=True, upload_to="images/")
    is_activated = models.CharField(max_length=10, choices=IS_AVAILABLE, default='true')
    
    def image_tag(self): # new
        return mark_safe('<img src="/../../media/%s" width="150" height="150" />' % (self.order_image))
    def save(self): # new
        super().save()
        if self.order_image:
            img = Im.open(self.order_image.path)
            # resize it
            if img.height > 300 or img.width > 300:
                output_size = (300,300)
                img.thumbnail(output_size)
                img.save(self.order_image.path)

class Coupon(models.Model):
    coupon_code = models.CharField(max_length=50, unique = True)
    coupon_name = models.CharField(max_length=50, unique = True)
    value_price = models.IntegerField(default = 0)
    discount_percent = models.IntegerField(default = 0)
    limited = models.BooleanField(default = True)
    number_of_time_to_expire = models.IntegerField(default = 1)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.now)


class CartItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.FloatField(blank=True)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)


class Invoice(models.Model):
    orders = models.ManyToManyField(Order, related_name = "ingredients")