from django.contrib import admin
from . models import Category

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('category_name',) }
    list_display = ('category_name', 'slug', 'description')
    # list_display_links = ('category_name', 'slug')
    # readonly_fields = ('description',)
    # ordering = ('-category_name',)
    
    # filter_horizontal = ()
    # list_filter= ()
    # fieldsets = ()

admin.site.register(Category, CategoryAdmin)