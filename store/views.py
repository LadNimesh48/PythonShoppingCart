from django.shortcuts import render, get_object_or_404
from . import views
from .models import Product
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q


# Create your views here.
def store(request, category_slug=None):
    products = None
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)  # Get category by slug
        products = Product.objects.filter(category=category, is_available=True).order_by('id')  # Ensure correct model field name (category, not Category)
        paginator = Paginator(products, 1)
        page = request.GET.get('page')
        page_product = paginator.get_page(page)
    else:
        products = Product.objects.filter(is_available=True).order_by('id')
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        page_product = paginator.get_page(page)

    context = {
        'products': page_product,
    }

    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        check_in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e
    
    context = {
        'single_product': single_product,
        'check_in_cart' : check_in_cart,
    }

    return render(request, 'store/product_detail.html', context)

def search(request):
    
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
        
        context = {
            'products': products,
        }
        
    
    return render(request, 'store/store.html', context)