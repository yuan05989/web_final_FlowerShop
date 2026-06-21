from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from orders.models import Order, OrderStatus
from orders.serializers import OrderCreateSerializer, OrderSerializer


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        return obj.user_id == request.user.id


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by("-id")
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        output = OrderSerializer(order)
        return Response(output.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status == OrderStatus.CANCELLED:
            return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

        order.status = OrderStatus.CANCELLED
        order.save(update_fields=["status", "updated_at"])
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
