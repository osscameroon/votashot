from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    path("api/docs/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    # Optional UI:
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-swagger",
    ),
    path(
        "api/docs/redoc/",
        SpectacularRedocView.as_view(url_name="api-schema"), name="api-redoc",
    ),
    #path("api/", include(("pro_auth.api_urls", "pro_auth"), namespace="api")),


    path('dashboard/', include(('core.dashboard_urls', 'core'), namespace='dashboard')),
    path('api/', include(('core.api_urls', 'core'), namespace='api')),

]