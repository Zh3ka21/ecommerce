import json
from urllib.parse import unquote
from .models import *

def cartData(request):
    if request.user.is_authenticated:
        try:
            customer = request.user.customer
        except Customer.DoesNotExist:
            customer = Customer.objects.create(
                user=request.user, 
                name=request.user.first_name,
                email=request.user.email
            )

        # Fetch or create order related to the customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items 
    else:
        # Handle unauthenticated users by using cookie data
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'items': items, 'order': order, 'cartItems': cartItems}

def cookieCart(request):
    # Get the cookie value and decode it
    cart_cookie = request.COOKIES.get('cart', '{}')
    decoded_cart = unquote(cart_cookie)  # Decode the URL-encoded string
    print(decoded_cart)
    
    try:
        cart = json.loads(decoded_cart)  # Now load the JSON
    except json.JSONDecodeError:
        cart = {}  # If there's an error, fall back to an empty cart
            
    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
    cartItems = order['get_cart_items'] 
    
    for i in cart:
        try:
            cartItems += cart[i]['quantity'] 
            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])
            
            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']
            
            item = {
                'product':{
                    'id':product.id,
                    'name':product.name, 
                    'price':product.price, 
                    'imageURL':product.imageURL
                    }, 
                'quantity':cart[i]['quantity'],
                'get_total':total,
            }
            items.append(item)
            
            if product.digital == False:
                order['shipping'] = True
        except:
            pass
    
    return {'items': items, 'order': order, 'cartItems': cartItems}

def guestOrder(request, data):
    print('User is not logged in..')
    print("cookiers: ", request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']
    
    cookieData = cookieCart(request)
    items = cookieData['items']
    
    customer, created = Customer.objects.get_or_create(name=name, email=email)
    customer.save()
    
    order = Order.objects.create(
        customer=customer,
        complete=False
    )
    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        
        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity=item['quantity']
        )
    return customer, order