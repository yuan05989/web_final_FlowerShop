from django.contrib import admin

from catalog.models import Category, FlowerKind, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)


@admin.register(FlowerKind)
class FlowerKindAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "festival", "type_list", "category", "price", "stock", "is_active", "created_at")
    list_filter = ("is_active", "category", "type")
    search_fields = ("name", "festival", "type__name")
    filter_horizontal = ("type",)

    @admin.display(description="Flower types")
    def type_list(self, obj):
        return ", ".join(obj.type.values_list("name", flat=True))
