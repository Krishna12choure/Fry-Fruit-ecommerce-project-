from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib import messages
from decimal import Decimal
from .models import *
import pdfkit


def home(request):
    featured_products = Product.objects.order_by('?')[:4]  # Fetch 4 random products
    return render(request, 'shop/home.html', {'featured_products': featured_products})


def about(request):
    return render(request, 'shop/about.html')


def products(request):
    all_products = Product.objects.all()
    return render(request, 'shop/products.html', {'products': all_products})


def gallery(request):
    gallery_images = GalleryImage.objects.all()
    return render(request, 'shop/gallery.html', {'gallery_images': gallery_images})


def blog(request):
    # Fetch all blog posts from the database
    blogs = Blog.objects.all().order_by('-publish_date')  # Fetching blog posts and ordering by the publish date
    return render(request, 'shop/blog.html', {'blogs': blogs})


def contact(request):
    return render(request, 'shop/contact.html')


@login_required
def add_to_cart(request, product_id):
    # Check if the user is logged in, if not, redirect to the login page with a message
    if not request.user.is_authenticated:
        messages.error(request, "Please log in or create an account to add items to your cart.")
        return redirect('login')  # Replace 'login' with the URL name for your login page

    # Get the product from the database
    product = get_object_or_404(Product, id=product_id)

    # Check if the product is already in the user's cart
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if not created:
        # If the item already exists, just increment the quantity
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"Added one more {product.name} to your cart.")
    else:
        # If the item is new, add it to the cart
        messages.success(request, f"Added {product.name} to your cart.")

    # Redirect to the products page
    return redirect('products')

@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.get_total_price() for item in cart_items)  # Fix method call
    return render(request, 'shop/cart/cart.html', {'cart_items': cart_items, 'total': total})


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('cart')


@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_amount = sum(item.get_total_price() for item in cart_items)

    # Define shipping charges and GST (for simplicity, you can modify it as per your logic)
    shipping_charges = Decimal('50.00')  # Example shipping charges
    gst = total_amount * Decimal('0.18')  # 18% GST

    # Calculate the total payable amount
    total_payable_amount = total_amount + shipping_charges + gst

    user = request.user  # Get the logged-in user

    if request.method == "POST":
        # Process the form for delivery details
        name = request.POST['name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        zip_code = request.POST['zip']
        address = request.POST['address']
        order_date = request.POST['order_date']
        payment_method = request.POST['payment_method']

        # Save delivery details to the database
        delivery_address = DeliveryAddress.objects.create(
            user=request.user,
            name=name,
            email=email,
            phone_number=phone_number,
            zip=zip_code,
            address=address,
            order_date=order_date
        )

        # Create the order
        order = Order.objects.create(
            user=request.user,
            total_amount=total_payable_amount,
            payment_method=payment_method
        )

        # Add items to the order
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.discount_price or item.product.price
            )

        # Clear the cart after placing the order
        cart_items.delete()

        # Add success message and redirect
        messages.success(request, "Order placed successfully!")
        return redirect('cart')  # Redirect to cart or any other page

    # Pass the user's data to the template
    return render(request, 'shop/cart/checkout.html', {
        'total_amount': total_amount,
        'shipping_charges': shipping_charges,
        'gst': gst,
        'total_payable_amount': total_payable_amount,
        'user': user
    })


@login_required
def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    html = render_to_string('shop/cart/invoice.html', {'order': order})

    pdf = pdfkit.from_string(html, False)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
    return response


def register_user(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken.")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.success(request, "Registration successful. Please log in.")
                return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")

    return render(request, 'auth/register.html')


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # If it's an admin, redirect to admin dashboard, else to user home
            if user.is_staff:
                messages.success(request, "Admin login successful!")
                return redirect('admin_dashboard')  # Admin dashboard view (can be customized)
            else:
                messages.success(request, "Login successful!")
                return redirect('home')  # User home page after login

        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'auth/login.html')


def logout_user(request):
    # If the user is an admin, log them out and redirect to the homepage
    if request.user.is_staff:
        logout(request)
        messages.success(request, "Admin has logged out successfully.")
        return redirect('home')  # Redirect to homepage after admin logs out

    # For normal users, simply log them out and redirect to the homepage
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')

@login_required
def dashboard(request):
    # Count the orders for each status
    total_orders = Order.objects.filter(user=request.user).count()
    pending_orders = Order.objects.filter(user=request.user, status='Pending').count()
    completed_orders = Order.objects.filter(user=request.user, status='Completed').count()
    canceled_orders = Order.objects.filter(user=request.user, status='Canceled').count()

    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'canceled_orders': canceled_orders,
    }

    return render(request, 'shop/user/dashboard.html', context)


def view_order(request, order_id):
    # Retrieve the order and its associated items
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)

    # Prepare a list of order items with calculated total for each item
    order_item_totals = []
    subtotal = Decimal(0)  # Initialize subtotal

    for item in order_items:
        total = Decimal(item.quantity) * Decimal(item.price)  # Calculate the total for each item
        subtotal += total  # Add to subtotal
        order_item_totals.append({
            'item': item,
            'total': total
        })

    # GST Calculation (18% of subtotal)
    gst = round(subtotal * Decimal(0.18), 2)

    # Fixed shipping charge
    shipping_charge = Decimal(50.00)

    # Total amount calculation
    total_amount = subtotal + gst + shipping_charge

    # Update the order instance
    order.subtotal = subtotal
    order.gst = gst
    order.shipping_charge = shipping_charge
    order.total_amount = total_amount
    order.save()

    # Pass data to the template
    return render(request, 'shop/user/view_order.html', {
        'order': order,
        'order_item_totals': order_item_totals,
        'grand_total': total_amount  # Ensuring grand total is correct
    })

@login_required
def cancel_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)

    # Convert Decimal to float before multiplication
    subtotal = sum(float(item.quantity) * float(item.price) for item in order_items)

    # GST Calculation (18% of subtotal)
    gst = Decimal(subtotal * 0.18).quantize(Decimal('0.01'))  # Convert to Decimal with 2 decimal places

    # Fixed shipping charge (Example: ₹50)
    shipping_charge = Decimal(50.00)

    # Total amount calculation
    total_amount = Decimal(subtotal) + gst + shipping_charge

    # Set canceled timestamp if not already set
    if not order.order_date:
        order.order_date = order.order_date  # Assuming `updated_at` is used for order updates

    # Update the order instance
    order.subtotal = Decimal(subtotal)
    order.gst = gst
    order.shipping_charge = shipping_charge
    order.total_amount = total_amount
    order.status = "Canceled"
    order.save()

    # Create a list of tuples with order item and its total
    order_item_totals = [
        (item, float(item.quantity) * float(item.price)) for item in order_items
    ]

    return render(request, 'shop/user/canceled_view.html', {
        'order': order,
        'order_item_totals': order_item_totals
    })

@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    for order in orders:
        order.items = OrderItem.objects.filter(order=order)
        for item in order.items:
            item.subtotal = item.quantity * item.price

    return render(request, 'shop/user/orders.html', {'orders': orders})

@login_required
def canceled_orders(request):
    canceled_orders = Order.objects.filter(
        user=request.user,
        status='Canceled'
    ).order_by('-created_at')


    return render(request, 'shop/user/canceled_orders.html', {'canceled_orders': canceled_orders})



@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.payment_status == False:  # Check if the order is not yet paid
        # Update order status to 'Canceled' instead of deleting it
        order.status = 'Canceled'
        order.save()
        messages.success(request, "Your order has been canceled.")
    else:
        messages.error(request, "This order cannot be canceled as it has already been paid.")

    return redirect('user_orders')
