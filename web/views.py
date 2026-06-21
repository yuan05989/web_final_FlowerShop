from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, FormView, ListView, TemplateView

from accounts.models import UserProfile
from catalog.models import Category, FlowerKind, Product
from orders.models import Cart, CartItem, Order, OrderItem, OrderStatus
from web.forms import CartAddForm, OrderCreateForm, RegisterForm


class ProductListView(ListView):
    model = Product
    template_name = "web/product_list.html"
    context_object_name = "products"
    paginate_by = 9

    def get_queryset(self):
        queryset = (
            Product.objects.select_related("category")
            .prefetch_related("type")
            .filter(is_active=True)
            .order_by("-created_at")
        )
        keyword = self.request.GET.get("q", "").strip()
        category_id = self.request.GET.get("category", "").strip()
        type_id = self.request.GET.get("type", "").strip()

        if keyword:
            queryset = queryset.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword))
        if category_id.isdigit():
            queryset = queryset.filter(category_id=int(category_id))
        if type_id.isdigit():
            queryset = queryset.filter(type__id=int(type_id))

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.order_by("name")
        context["flower_types"] = FlowerKind.objects.order_by("name")
        context["q"] = self.request.GET.get("q", "")
        context["current_category"] = self.request.GET.get("category", "")
        context["current_type"] = self.request.GET.get("type", "")
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "web/product_detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.select_related("category").prefetch_related("type").filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart_form"] = CartAddForm()
        return context


class RegisterPageView(FormView):
    template_name = "registration/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("web:product-list")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password1"])
        user.save()

        UserProfile.objects.create(
            user=user,
            phone=form.cleaned_data.get("phone", ""),
            address=form.cleaned_data.get("address", ""),
        )

        login(self.request, user)
        messages.success(self.request, "Registration successful. Welcome to FlowerShop.")
        return super().form_valid(form)


class UserLoginView(LoginView):
    template_name = "registration/login.html"


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("web:product-list")


class OrderCreateView(LoginRequiredMixin, FormView):
    form_class = OrderCreateForm

    def post(self, request, *args, **kwargs):
        self.object = get_object_or_404(Product, pk=kwargs["pk"], is_active=True)
        form = self.get_form()
        if not form.is_valid():
            messages.error(request, "Please enter a valid quantity.")
            return redirect("web:product-detail", pk=self.object.pk)

        quantity = form.cleaned_data["quantity"]

        with transaction.atomic():
            product = Product.objects.select_for_update().get(pk=self.object.pk)
            if not product.is_active:
                messages.error(request, "This product is no longer available.")
                return redirect("web:product-detail", pk=product.pk)
            if quantity > product.stock:
                messages.error(request, f"Insufficient stock. Available quantity: {product.stock}.")
                return redirect("web:product-detail", pk=product.pk)

            order = Order.objects.create(user=request.user, total_amount=Decimal("0.00"))
            line_total = product.price * quantity
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.price,
                line_total=line_total,
            )

            order.total_amount = line_total
            order.save(update_fields=["total_amount"])

            product.stock -= quantity
            product.save(update_fields=["stock", "updated_at"])

        messages.success(request, f"Order created successfully. Order #{order.id}.")
        return redirect("web:order-detail", pk=order.pk)


class CartAddView(LoginRequiredMixin, FormView):
    form_class = CartAddForm

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=kwargs["pk"], is_active=True)
        form = self.get_form()
        if not form.is_valid():
            messages.error(request, "Please enter a valid quantity.")
            return redirect("web:product-detail", pk=product.pk)

        quantity = form.cleaned_data["quantity"]
        cart, _ = Cart.objects.get_or_create(user=request.user)
        existing_quantity = CartItem.objects.filter(cart=cart, product=product).values_list("quantity", flat=True).first() or 0
        if existing_quantity + quantity > product.stock:
            messages.error(request, f"Insufficient stock. Available quantity: {product.stock}.")
            return redirect("web:product-detail", pk=product.pk)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity},
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save(update_fields=["quantity", "updated_at"])

        messages.success(request, f"{product.name} added to your cart.")
        return redirect("web:cart-list")


class CartListView(LoginRequiredMixin, TemplateView):
    template_name = "web/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        context["cart"] = cart
        context["cart_items"] = cart.items.select_related("product").order_by("-created_at")
        context["cart_total"] = cart.total_amount
        return context


class CartClearView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        messages.success(request, "Your cart has been cleared.")
        return redirect("web:cart-list")


class CartCheckoutView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)

        with transaction.atomic():
            cart_items = list(
                cart.items.select_related("product")
                .select_for_update()
                .order_by("id")
            )
            if not cart_items:
                messages.error(request, "Your cart is empty.")
                return redirect("web:cart-list")

            product_ids = [item.product_id for item in cart_items]
            products = Product.objects.select_for_update().filter(id__in=product_ids, is_active=True)
            product_map = {product.id: product for product in products}

            for item in cart_items:
                product = product_map.get(item.product_id)
                if not product:
                    messages.error(request, f"{item.product.name} is no longer available.")
                    return redirect("web:cart-list")
                if item.quantity > product.stock:
                    messages.error(request, f"Insufficient stock for {product.name}. Available quantity: {product.stock}.")
                    return redirect("web:cart-list")

            order = Order.objects.create(user=request.user, total_amount=Decimal("0.00"))
            total = Decimal("0.00")
            for item in cart_items:
                product = product_map[item.product_id]
                line_total = product.price * item.quantity
                total += line_total
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    unit_price=product.price,
                    line_total=line_total,
                )
                product.stock -= item.quantity
                product.save(update_fields=["stock", "updated_at"])

            order.total_amount = total
            order.save(update_fields=["total_amount"])
            cart.items.all().delete()

        messages.success(request, f"Checkout complete. Order #{order.id}.")
        return redirect("web:order-detail", pk=order.pk)


class OrderCancelView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=kwargs["pk"], user=request.user)
        if order.status != OrderStatus.CANCELLED:
            order.status = OrderStatus.CANCELLED
            order.save(update_fields=["status", "updated_at"])
            messages.success(request, f"Order #{order.id} has been cancelled.")
        else:
            messages.info(request, f"Order #{order.id} was already cancelled.")
        return redirect("web:order-detail", pk=order.pk)


class MyOrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "web/order_list.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")


class MyOrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "web/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product")
