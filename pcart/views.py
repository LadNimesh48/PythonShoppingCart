from django.shortcuts import render
from store.models import Product

def home(request):
    
    products = Product.objects.all().filter(is_available = True)
    print(products)
    context = {
        'products' : products,
    }
    print(context)
    return render(request, 'home.html', context)