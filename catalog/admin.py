from django.contrib import admin

from catalog.models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "stock", "is_active", "created_at")
    list_filter = ("is_active", "category")
    search_fields = ("name",)
