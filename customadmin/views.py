from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from shop.models import *
from datetime import datetime
from decimal import Decimal
from .forms import *
from django.contrib import messages
from .decorators import admin_required
from django.core.paginator import Paginator

@admin_required
def customadmin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # If authentication is successful, log the user in
            login(request, user)
            return redirect('customadmin_dashboard')  # Redirect to logged-in page
        else:
            # If authentication fails, show an error message
            messages.error(request, "Invalid username or password.")
            return render(request, 'customadmin/admin_login.html')

    return render(request, 'customadmin/admin_login.html')
@admin_required
def customadmin_logout(request):
    logout(request)
    return redirect('home')

@login_required
def customadmin_dashboard(request):
    # Total Users
    total_users = User.objects.count()

    # Total Products
    total_products = Product.objects.count()

    # Total Payment (sum of all orders' total_amount)
    total_payment = Order.objects.aggregate(total_payment=models.Sum('total_amount'))['total_payment'] or 0

    # Today's Orders (orders placed today)
    today = date.today()
    todays_orders = Order.objects.filter(order_date=today).count()

    context = {
        'total_users': total_users,
        'total_products': total_products,
        'total_payment': total_payment,
        'todays_orders': todays_orders,
    }

    return render(request, 'customadmin/admin_dashboard.html', context)

# Add Product View
@admin_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('product_management')
    else:
        form = ProductForm()
    return render(request, 'product/add_product.html', {'form': form})

# List Products View
@admin_required
def product_management(request):
    products = Product.objects.all()
    return render(request, 'product/product_management.html', {'products': products})

# Edit Product View
@admin_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_management')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product/add_product.html', {'form': form, 'product': product})

# Delete Product View
@admin_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, 'Product deleted successfully!')
    return redirect('product_management')

@admin_required
def discount_management(request):
    # Get the search query from GET request
    search_query = request.GET.get('search', '')

    # Filter products based on the search query (if any)
    if search_query:
        products = Product.objects.filter(name__icontains=search_query)  # Case-insensitive search
    else:
        products = Product.objects.all()

    # Paginate the products
    paginator = Paginator(products, 10)  # Show 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Handle POST request for updating discount prices
    if request.method == 'POST':
        for product in products:
            discount_price = request.POST.get(f'discount_price_{product.id}')
            if discount_price:
                product.discount_price = discount_price
                product.save()
        return redirect('discount_management')  # Redirect to prevent resubmission

    return render(request, 'product/discount_management.html', {
        'products': page_obj,
        'search_query': search_query,  # Pass the search query back to the template
    })
# View to list gallery images
@admin_required
def gallery_list(request):
    gallery_images = GalleryImage.objects.all()
    return render(request, 'gallery/gallery_list.html', {'gallery_images': gallery_images})

# View to add a new image to the gallery
@admin_required
def gallery_add(request):
    if request.method == 'POST':
        form = GalleryImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('gallery_list')
    else:
        form = GalleryImageForm()
    return render(request, 'gallery/gallery_add.html', {'form': form})

# View to edit an existing gallery image
@admin_required
def gallery_edit(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)
    if request.method == 'POST':
        form = GalleryImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            return redirect('gallery_list')
    else:
        form = GalleryImageForm(instance=image)
    return render(request, 'gallery/gallery_edit.html', {'form': form})

# View to delete an image from the gallery
@admin_required
def gallery_delete(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)
    image.delete()
    return redirect('gallery_list')


# List all blogs
@admin_required
def blog_list(request):
    blogs = Blog.objects.all()
    return render(request, 'blog/blog_list.html', {'blogs': blogs})

# Add a new blog
def add_blog(request):
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('blog_list')
    else:
        form = BlogForm()
    return render(request, 'blog/add_blog.html', {'form': form, 'action': 'Add'})

# Edit an existing blog
@admin_required
def edit_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES, instance=blog)  # Pass request.FILES to handle image upload
        if form.is_valid():
            form.save()
            return redirect('blog_list')
    else:
        form = BlogForm(instance=blog)
    return render(request, 'blog/edit_blog.html', {'form': form, 'action': 'Edit', 'blog': blog})

# Delete a blog
@admin_required
def delete_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    blog.delete()
    return redirect('blog_list')



@admin_required
def all_orders(request):
    if not request.user.is_superuser:  # Only allow admins
        return redirect('user_orders')

    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'orders/admin_orders.html', {'orders': orders})

@admin_required
def order_detail(request, order_id):
    """Allow users to see their own orders & admins to see all orders"""
    if request.user.is_superuser:
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, user=request.user)

    order_items = OrderItem.objects.filter(order=order)

    # Manually add total price to each item
    order_items_with_total = []
    for item in order_items:
        item.total_price = item.quantity * item.price
        order_items_with_total.append(item)

    # Get the latest delivery address for the user
    delivery_address = DeliveryAddress.objects.filter(user=order.user).order_by('-order_date').first()

    return render(
        request,
        'orders/order_detail.html',
        {'order': order, 'order_items': order_items_with_total, 'delivery_address': delivery_address}
    )


@admin_required
def update_order_status(request, order_id, status):
    if not request.user.is_superuser:
        return redirect('user_orders')

    # Get the order object
    order = get_object_or_404(Order, id=order_id)

    # Check if the new status is "Completed"
    if status == 'Completed':
        order.status = 'Completed'
        order.payment_status = True  # Change payment status to Paid
        order.save()

    # Handle other status updates if needed
    else:
        order.status = status
        order.save()

    return redirect('all_orders')

@admin_required
def generate_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    # Ensure the delivery address exists
    delivery_address = DeliveryAddress.objects.filter(order=order).order_by('-order_date').first()
    if not delivery_address:
        delivery_address = DeliveryAddress.objects.filter(user=order.user).order_by('-order_date').first()

    # Calculate GST and Total Payable Amount
    gst_rate = Decimal('0.18')
    shipping_charges = Decimal('5.00')

    gst_amount = (order.total_amount * gst_rate).quantize(Decimal('0.01'))
    payable_total = ((order.total_amount * Decimal('1.18')) + shipping_charges).quantize(Decimal('0.01'))

    context = {
        'order': order,
        'order_items': order_items,
        'delivery_address': delivery_address,  #  Pass delivery address to template
        'invoice_date': datetime.today().strftime('%Y-%m-%d'),
        'gst_amount': gst_amount,
        'payable_total': payable_total
    }
    return render(request, 'customadmin/invoice.html', context)
