from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('products/', products, name='products'),
    path('gallery/', gallery, name='gallery'),
    path('blog/', blog, name='blog'),
    path('contact/', contact, name='contact'),

    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),

    path('cart/', cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', remove_from_cart, name='remove_from_cart'),

    path('checkout/', checkout, name='checkout'),
    path('order-summary/<int:order_id>/', order_summary, name='order_summary'),

    path('dashboard/', dashboard, name='dashboard'),
    path('orders/', user_orders, name='user_orders'),
    path('order/<int:order_id>/', view_order, name='view_order'),
    path('canceled-orders/', canceled_orders, name='canceled_orders'),
    path('cancel-order/<int:order_id>/', cancel_order, name='cancel_order'),
    path('cancel-order-view/<int:order_id>/', cancel_view, name='cancel_view'),

]
