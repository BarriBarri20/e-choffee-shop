import json
import random
import string
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from .models import User, Order, Ingredient, Coupon, Cart, CartItem
from .forms import OrderUploadForm, IngredientUploadForm
from paypal.standard.forms import PayPalPaymentsForm

# Create your views here.

'''This the index page here'''
def make_payment(request, price, invoice_id, custom):
    # What you want the button to do.
    paypal_dict = {
        "business": "receiver_email@example.com",
        "amount": "10000000.00",
        "item_name": "name of the item",
        "invoice": "unique-invoice-id",
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return": request.build_absolute_uri(reverse('your-return-view')),
        "cancel_return": request.build_absolute_uri(reverse('your-cancel-view')),
        "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
    }

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"form": form}
    return render(request, "payment.html", context)


def index(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            order_data = Order.objects.all()
            ingredient_data = Ingredient.objects.all()
            context = {
                        'order_data' : order_data,
                        'ingredient_data' : ingredient_data
            }
            return render(request, "admin.html", context)
    return render(request, "index.html", {
        "user_is_registred": request.user.is_authenticated
    })


'''This function check if the user is logged in otherwise the login page for new users'''
def login_view(request):
    # Check if the user is logged in
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if request.method == "POST":
        username = request.POST["username"].lower()
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        # if user authentication success
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "login.html", {
                "message": "Invalid username and/or password"
            })
    return render(request, "login.html", {"user": request.user.username})


'''This function redirect the user to the registration page'''
def register_view(request):
    # Check if the user is logged in
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if request.method == "POST":
        first_name = request.POST["first_name_to_django"]
        last_name = request.POST["last_name_to_django"]
        password = request.POST["password"]
        password_confiramtion = request.POST["password_confirmation"]
        birth_date = request.POST["birth_date"]
        email = request.POST["email"]
        phone_number = request.POST["phone_number"]

        # check if the password is the same as confirmation
        if password != password_confiramtion:
                return render(request, "test_register.html", {
                "message": "Passwords must match."
            })
        # Checks if the username is already in use
        if User.objects.filter(email=email).count() == 1:
            return render(request, "test_register.html", {
                "message": "Email already taken."
            })
        try:
            user = User.objects.create_user(username=first_name.lower() + last_name.lower(), first_name=first_name, last_name=last_name,
                                            password=password, email=email, date_of_birth=birth_date, number_of_orders=0, phone_number=phone_number)
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        except IntegrityError:
            return render(request, "test_register.html", {
                "message": "Username already taken!"
            })
    return render(request, "test_register.html")

def orders(request):
    orders_data = Order.objects.all()
    ingredient_data = Ingredient.objects.all()
    context = {
        'orders_data' : orders_data,
    }
    return render(request, "orders.html", context)

def add_order_cart(request, order_slug):
    return render(request, )

def cart_show(request):
    return render(request)
'''This is the logout function for user'''
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def test_register(request):
    return render(request, 'test_register.html')


'''This is will create a template of order page'''
def create_order(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        slug = ''.join(random.choice(string.ascii_letters) for x in range(20))
        data = json.loads(request.body)
        name = data["name"]
        order_description = "Change this description here!"
        ingredient_name = "Name of the ingredient here!"
        initial_ingredient = Ingredient(name=ingredient_name)
        initial_ingredient.save()
        order = Order(slug=slug, name=name,
                      description=order_description)
        order.save()
        order.order_ingredients.add(initial_ingredient)
        order.save()
        return JsonResponse({"message": "Sucess", "slug": slug})

def create_ingredient(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
    if request.method == "POST":
        ingredient_slug = ''.join(random.choice(string.ascii_letters) for x in range(20))
        data = json.loads(request.body)
        ingredient_name = data["name"]
        ingredient = Ingredient(ingredient_slug=ingredient_slug, name=ingredient_name)
        ingredient.save()
        return JsonResponse({"message": "Sucess", "ingredient_slug": ingredient_slug})


""" Extract the order element to HTML"""
def edit_order(request, slug):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    orderInfo = Order.objects.filter(slug=slug)
    # Checking if order still exists
    if orderInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else:
        orderInfo = orderInfo[0]
    if request.method == 'POST':
        form = OrderUploadForm(request.POST, request.FILES, instance=orderInfo)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = OrderUploadForm(instance=orderInfo)
    return render(request, 'edit_order.html', {'form': form})




""" Extract the ingredient element to HTML"""
def edit_ingredient(request, ingredient_slug):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    ingredientInfo = Ingredient.objects.filter(ingredient_slug=ingredient_slug)
    # Checking if ingredient still exists
    if ingredientInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    else:
        ingredientInfo = ingredientInfo[0]
    if request.method == 'POST':
        form = IngredientUploadForm(request.POST, request.FILES, instance=ingredientInfo)
        order_ingredients = request.POST.getlist('ingredients')
        for ingredient in order_ingredients:
            if Ingredient.objects.filter(id=ingredient).exists():
                ingredient = Ingredient.objects.get(id=ingredient)
                form.order_ingredients.add(ingredient)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = IngredientUploadForm(instance=ingredientInfo)
    return render(request, 'edit_ingredient.html', {'form': form})




def delete_order(request, slug):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
    orderInfo = Order.objects.filter(slug=slug)
    if orderInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    orderInfo = orderInfo[0]

    if request.method == "DELETE":
        orderInfo.delete()
        return JsonResponse({"message" : "success"})


def delete_ingredient(request, ingredient_slug):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("403"))
    ingredientInfo = Ingredient.objects.filter(ingredient_slug=ingredient_slug)
    if ingredientInfo.count() == 0:
        return HttpResponseRedirect(reverse("404"))
    ingredientInfo = ingredientInfo[0]

    if request.method == "DELETE":
        ingredientInfo.delete()
        return JsonResponse({"message" : "success"})


"""View order"""
def view_order(request, slug):
    orderInfo = Order.objects.filter(slug=slug)
    # Checking if order exists
    if orderInfo.count() == 0:
        return HttpResponseRedirect(reverse('404'))
    else:
        orderInfo = orderInfo[0]
    if orderInfo.authenticated_responder:
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))
    return render(request, "view_order.html", {
        "order": orderInfo
    })


@login_required
def add_to_cart(request, slug):
    order = get_object_or_404(Order, slug=slug)
    cart, created = Cart.objects.get_or_create(user=request.user)
    order, created = CartItem.objects.get_or_create(order=order, cart=cart)
    order.quantity += 1
    order.save()
    messages.success(request, "Cart updated!")
    return redirect('cart')

@login_required
def delete_from_cart(request, slug, pk):
    order, created = get_object_or_404(Order, slug=slug)
    order = CartItem.objects.get(order=order, pk=pk)
    if order.quantity == 1:
        order.delete()
    else:
        order.quantity -= 1
        order.save()
    return redirect("cart") 

@login_required
def cart_view(request):
    data = Cart.objects.all()
    data = {'data':data}
    return render(request, "cart.html", data)