from decimal import Decimal

from rest_framework import serializers

from catalog.models import Product
from orders.models import Order, OrderItem


class OrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "unit_price", "line_total"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "status", "total_amount", "items", "created_at", "updated_at"]
        read_only_fields = ["user", "total_amount"]


class OrderCreateSerializer(serializers.Serializer):
    items = OrderItemInputSerializer(many=True)

    def create(self, validated_data):
        request = self.context["request"]
        order = Order.objects.create(user=request.user)

        total = Decimal("0.00")
        items_data = validated_data["items"]

        for item in items_data:
            product = Product.objects.get(pk=item["product_id"])
            quantity = item["quantity"]
            unit_price = product.price
            line_total = unit_price * quantity
            total += line_total

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                line_total=line_total,
            )

        order.total_amount = total
        order.save(update_fields=["total_amount"])
        return order

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order items cannot be empty")

        product_ids = [item["product_id"] for item in value]
        products = Product.objects.filter(id__in=product_ids, is_active=True)
        product_map = {product.id: product for product in products}

        for item in value:
            product = product_map.get(item["product_id"])
            if not product:
                raise serializers.ValidationError(f"Product {item['product_id']} not found or inactive")
            if item["quantity"] > product.stock:
                raise serializers.ValidationError(
                    f"Product {product.id} stock insufficient: requested {item['quantity']}, available {product.stock}"
                )

        return value
