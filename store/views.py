from django.shortcuts import get_object_or_404, redirect, render
from .models import Product, Order, OrderItem, ShippingAddress, Customer
from .utils import cookieCart, cartData, guestOrder
from .forms import CustomUserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from django.core.paginator import Paginator
from django.db.models import Q

import json
import datetime
from .forms import LoginForm


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)            
            return redirect('store')
        else:
            print(form.errors)
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    
    data = cartData(request)
    cartItems = data['cartItems']
    return render(request, 'auth/register.html', {'form': form, 'cartItems': cartItems})

def login_view(request):
    """Handle user login."""
    form = LoginForm(request.POST or None)  # Instantiate the login form
    context = {}

    # Get cart data
    data = cartData(request)
    cartItems = data['cartItems']
    context['form'] = form
    context['cartItems'] = cartItems  # Pass cart items to the template

    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']  # Get username from form
        password = form.cleaned_data['password']  # Get password from form
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)  # Log the user in
            return redirect('store')  # Redirect to store or desired page
        else:
            # Show a message for invalid credentials
            messages.error(request, 'Invalid username or password.')

    return render(request, 'auth/login.html', context)

def logout_view(request):
    logout(request)
    return redirect('login') 

def store(request):
    data = cartData(request)
    cartItems = data['cartItems'] 
    
    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)

def product_detail(request, product_id):
    data = cartData(request)
    cartItems = data['cartItems'] 
    product = get_object_or_404(Product, id=product_id)
    context = {'product': product, 'cartItems': cartItems}
    
    print(context)
    return render(request, 'store/product.html', context)

def cart(request):
    data = cartData(request)
    
    cartItems = data['cartItems']
    order = data['order']
    items = data['items'] 
    
    context = {'items': items, 'order': order, 'cartItems': cartItems}    
    return render(request, 'store/cart.html', context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']       
        
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
 
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)
    
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
	)

    return JsonResponse('Payment submitted..', safe=False)

def search(request):
    search_query = request.GET.get('q', '').strip()
    data = cartData(request)
    cartItems = data['cartItems'] 

    if search_query:
        price_query = None
        try:
            price_query = float(search_query.replace(',', '.'))
        except ValueError:
            pass
        
        filters = Q(name__icontains=search_query)
        if price_query is not None:
            filters |= Q(price=price_query)

        products = Product.objects.filter(filters).order_by('name')
    else:
        products = Product.objects.all().order_by('name')

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    context = {'products': products_page, 'cartItems': cartItems, 'search_query': search_query}

    return render(request, 'store/store.html', context)

def orderby(request):
    data = cartData(request)
    cartItems = data['cartItems'] 
    
    search_query = request.GET.get('q', '')
    order_by = request.GET.get('order_by', 'price')
    min_price = request.GET.get('min_price') 
    max_price = request.GET.get('max_price')

    products = Product.objects.all()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    if order_by:
        products = products.order_by(order_by)

    context = {
        'products': products,
        'search_query': search_query,
        'order_by': order_by,
        'min_price': min_price,
        'max_price': max_price,
        'cartItems': cartItems,
    }
    return render(request, 'store/store.html', context)

