from django.urls import path

from web.views import (
    MyOrderDetailView,
    MyOrderListView,
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
    path("orders/", MyOrderListView.as_view(), name="order-list"),
    path("orders/<int:pk>/", MyOrderDetailView.as_view(), name="order-detail"),
    path("register/", RegisterPageView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
]
