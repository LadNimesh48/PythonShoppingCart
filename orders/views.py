from django.shortcuts import render, redirect
from carts.models import Cart, CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
from store.models import Product, Category
import datetime
import json
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import JsonResponse
# Create your views here.

def payments(request):
    
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body.orderID)
    # Store payment details into payment Model
    
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_methos'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()
    
    # move the cart items to Order Product Table
    cart_items = CartItem.objects.filter(user=request.user)
    
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        # now variations update after save details using id
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all() #store the variations of user request in product_variation variable
        
        orderproduct = OrderProduct.objects.get(id=orderproduct.id) # get the details using line 39 save data fetch details using id
        # update variations 
        orderproduct.variations.set(product_variation)
        orderproduct.save()
        
        
    
        # Reduce Quantity of the sold Products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
    
    
    # Clear Cart
    CartItem.objects.filter(user=request.user).delete()
    
    # send order recived email to customer
    mail_subject = 'Thank you for your order !'
    message      = render_to_string('orders/order_recived_email.html'),{
        'user'   : request.user,
        order    : order          
    }
    to_email     = request.user.email
    send_email   = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()
    
    # send order number and transactionID back to sendData Method via JSONResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)
    
    
    return render(request, 'orders/payments.html')

def place_order(request, total=0, quantity=0):
    current_user = request.user
    # print(current_user)
    
    # if the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    # print(cart_count)
    if cart_count <= 0:
        return redirect('store')
    
    # return HttpResponse('ok')
    
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += ( cart_item.product.price * cart_item.quantity )
        quantity += cart_item.quantity
    tax = (18 * total)/100
    grand_total = total + tax
        
        
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # store all the billing information inside Order Table
            data = Order()
            # print(data)
            # print(form)
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip=request.META.get('REMOTE_ADDR')
            data.save()
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20250330
            # return HttpResponse('ok')
            order_number = current_date + str(data.id) #id will come becouse line number 50 we save data 
            data.order_number = order_number
            data.save()
            # print('data save')
            order = Order.objects.filter(user=current_user, is_ordered=False, order_number=order_number).first()
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            # print(context)
            return render(request, 'orders/payments.html', context)
        else:
            print("Form errors:", form.errors)
            # print('Validation error')
            return redirect('checkout')
    else:
        print('Not Post Value')
        return redirect('checkout')


def order_complete(request):
    
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        order_product = OrderProduct.objects.filter(order=order.id)
        
        subtotal = 0
        for i in order_product:
            subtotal += i.product_price * i.quantity
        
        Payments = Payment.objects.get(payment_id=transID)
        
        context = {
            'order' : order,
            'order_product' : order_product,
            'order_number' : order.order_number,
            'transID' : Payments.payment_id,
            'Payment' : Payments,
            'subtotal' : subtotal,
            
        }
        return redirect(request, 'orders/order_complete.html', context)
        
    except (Order.DoesNotExist, Payment.DoesNotExist):
        return redirect('home')
