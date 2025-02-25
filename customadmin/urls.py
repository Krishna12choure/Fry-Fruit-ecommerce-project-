from django.urls import path
from .views import *

urlpatterns = [
    path("login/", customadmin_login, name="customadmin_login"),
    path("logout/", customadmin_logout, name="customadmin_logout"),
    path("dashboard/", customadmin_dashboard, name="customadmin_dashboard"),

    path('product/add/', add_product, name='add_product'),  # Add Product
    path('product/list/', product_management, name='product_list'),  # List Products
    path('product/edit/<int:product_id>/', edit_product, name='edit_product'),  # Edit Product
    path('product/delete/<int:product_id>/', delete_product, name='delete_product'),

    path('discount-management/', discount_management, name='discount_management'),

    path('gallery/', gallery_list, name='gallery_list'),
    path('gallery/add/', gallery_add, name='gallery_add'),
    path('gallery/edit/<int:pk>/', gallery_edit, name='gallery_edit'),
    path('gallery/delete/<int:pk>/', gallery_delete, name='gallery_delete'),

    path('list/', blog_list, name='blog_list'),
    path('add/', add_blog, name='add_blog'),
    path('edit/<int:pk>/', edit_blog, name='edit_blog'),
    path('delete/<int:pk>/', delete_blog, name='delete_blog'),

    path('orders/', all_orders, name='all_orders'),
    path('orders/<int:order_id>/', order_detail, name='order_detail'),
    path('orders/update/<int:order_id>/<str:status>/', update_order_status, name='update_order_status'),

    path('invoice/<int:order_id>/', generate_invoice, name='generate_invoice'),


]
