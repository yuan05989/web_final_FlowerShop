from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


def api_root(_request):
    return JsonResponse(
        {
            "message": "FlowerShop API",
            "version": "v1",
            "docs": "/swagger/",
            "schema": "/api/schema/",
        }
    )


urlpatterns = [
    path("", include("web.urls")),
    path("admin/", admin.site.urls),
    path("api/", api_root, name="api-root"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/", include("catalog.urls")),
    path("api/v1/", include("orders.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
