from rest_framework import serializers

from catalog.models import Category, FlowerKind, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "created_at", "updated_at"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    type = serializers.PrimaryKeyRelatedField(queryset=FlowerKind.objects.all(), many=True, required=False)
    type_names = serializers.SlugRelatedField(source="type", many=True, read_only=True, slug_field="name")

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "category_name",
            "name",
            "festival",
            "type",
            "type_names",
            "description",
            "price",
            "stock",
            "is_active",
            "image",
            "created_at",
            "updated_at",
        ]
