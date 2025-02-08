from category.models import Category

def all_category(request):
    all_category = Category.objects.all()
    return dict(Allcategory=all_category)
    