from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product, Variation
from carts.models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    # if the user is Authenticated
    if current_user.is_authenticated:
        product_variations = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product ,variation_category__iexact=key, variation_value__iexact=value)
                    product_variations.append(variation)
                    # print(variation)
                except:
                    pass
                
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            # existing variation -> from Database
            # current Variations -> product_variations
            # item_id -> From database
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            
            if product_variations in ex_var_list:
                # increse Quantity in in same id
                index = ex_var_list.index(product_variations)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            
            
            else:
                # Create new Cart item 
                item = CartItem.objects.create(product=product, quantity = 1, user=current_user)
                if len(product_variations) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variations)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                user = current_user,
                quantity = 1, 
            )
            if len(product_variations) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variations)
            cart_item.save()
        return redirect('cart')
    # if the user is Not Authenticated   
    else:
        product_variations = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product ,variation_category__iexact=key, variation_value__iexact=value)
                    product_variations.append(variation)
                    # print(variation)
                except:
                    pass
        
        
        # print(product)
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart using the cart_id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()
        
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            # existing variation -> from Database
            # current Variations -> product_variations
            # item_id -> From database
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            
            if product_variations in ex_var_list:
                # increse Quantity in in same id
                index = ex_var_list.index(product_variations)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            
            
            else:
                # Create new Cart item 
                item = CartItem.objects.create(product=product, quantity = 1, cart=cart)
                if len(product_variations) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variations)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                cart = cart,
                quantity = 1, 
            )
            if len(product_variations) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variations)
            cart_item.save()
        return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')
    


def cart(request, quantity=0, total=0, cart_item=None):
    try:
        cart_items = []
        tax = 0
        grad_total = 0
        
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)    
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        tax = (18 * total)/100
        grad_total = (total + tax)
    except ObjectDoesNotExist:
        pass 
    
    context = {
        'total' : total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grad_total': grad_total,
    }
    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request, quantity=0, total=0, cart_item=None):
    try:
        cart_items = []
        tax = 0
        grad_total = 0
        if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user=request.user, is_active=True)    
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        tax = (18 * total)/100
        grad_total = (total + tax)
    except ObjectDoesNotExist:
        pass 
    
    context = {
        'total' : total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grad_total': grad_total,
    }
    return render(request, 'store/checkout.html', context)