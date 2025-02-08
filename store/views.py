from django.shortcuts import render, get_object_or_404
from . import views
from .models import Product
from category.models import Category

# Create your views here.
def store(request, category_slug=None):
    products = None
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)  # Get category by slug
        products = Product.objects.filter(category=category, is_available=True)  # Ensure correct model field name (category, not Category)
    else:
        products = Product.objects.filter(is_available=True)

    context = {
        'products': products,
    }

    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e:
        raise e
    
    context = {
        'single_product': single_product,
    }

    
    return render(request, 'store/product_detail.html', context)