from django.urls import path

from web.views import (
    CartAddView,
    CartCheckoutView,
    CartClearView,
    CartListView,
    MyOrderDetailView,
    MyOrderListView,
    OrderCancelView,
    OrderCreateView,
    ProductDetailView,
    ProductListView,
    RegisterPageView,
    UserLoginView,
    UserLogoutView,
)

app_name = "web"

urlpatterns = [
    path("", ProductListView.as_view(), name="product-list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("products/<int:pk>/order/", OrderCreateView.as_view(), name="order-create"),
    path("products/<int:pk>/cart/add/", CartAddView.as_view(), name="cart-add"),
    path("cart/", CartListView.as_view(), name="cart-list"),
    path("cart/clear/", CartClearView.as_view(), name="cart-clear"),
    path("cart/checkout/", CartCheckoutView.as_view(), name="cart-checkout"),
    path("orders/", MyOrderListView.as_view(), name="order-list"),
    path("orders/<int:pk>/", MyOrderDetailView.as_view(), name="order-detail"),
    path("orders/<int:pk>/cancel/", OrderCancelView.as_view(), name="order-cancel"),
    path("register/", RegisterPageView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
]
