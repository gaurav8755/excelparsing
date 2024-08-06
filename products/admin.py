from django.contrib import admin
from .models import Product, ProductVariation

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'lowest_price', 'last_updated')
    search_fields = ('name',)

@admin.register(ProductVariation)
class ProductVariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_text', 'stock', 'last_updated')
    search_fields = ('variation_text',)
