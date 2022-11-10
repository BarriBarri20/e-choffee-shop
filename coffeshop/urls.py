from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views


urlpatterns = [
    path('', views.index, name="index"),
    path('login', views.login_view, name="login"),
    path('register', views.register_view, name="register"),
    path('logout', views.logout_view, name='logout'),
    path('orders', views.orders, name="orders"),
    path('test_register', views.test_register, name='test_register'),
    path('order/create', views.create_order, name="create_order"),
    path('ingredient/create', views.create_ingredient, name="create_ingredient"),
    path('order', views.view_order, name='order'),
    
    path('order/<str:slug>/edit', views.edit_order, name="edit_order"),
    path('ingredient/<str:ingredient_slug>/edit', views.edit_ingredient, name="edit_ingredient"),

    path('order/<str:slug>/delete', views.delete_order, name="delete_order"),
    path('ingredient/<str:ingredient_slug>/delete', views.delete_ingredient, name="delete_ingredient"),

    path('cart/<str:slug>/add_to_cart', views.add_to_cart, name="add_to_cart"),
    path('cart/<str:slug>/delete_from_cart', views.delete_from_cart, name="delete_from_cart"),
    path('cart/', views.cart_view, name="cart"),

    path('paypal/', include("paypal.standard.ipn.urls")),

    *static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT),
    *static(settings.STATIC_URL,document_root = settings.STATIC_ROOT),
]