"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from two_factor.urls import urlpatterns as tf_urls
from two_factor.admin import AdminSiteOTPRequired
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from shared.views import health_check

admin.site.__class__ = AdminSiteOTPRequired

urlpatterns = [
    path('', include(tf_urls)),
    path(settings.ADMIN_URL_PATH, admin.site.urls),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('land/', include('apps.land.urls')),
    path('crops/', include('apps.crops.urls')),
    path('loans/', include('apps.loans.urls')),
    path('escrow/', include('apps.escrow.urls')),
    path('insurance/', include('apps.insurance.urls')),
    path('inputs/', include('apps.inputs.urls')),
    path('contracts/', include('apps.contracts.urls')),
    path('delivery/', include('apps.delivery.urls')),
    path('settlements/', include('apps.settlements.urls')),
    path('wallets/', include('apps.wallets.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('community/', include('apps.community.urls')),
    path('credit/', include('apps.credit.urls')),
    path('assistant/', include('apps.assistant.urls')),
    path('schema/', SpectacularAPIView.as_view(), name = 'schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name = 'schema'), name = 'swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name = 'schema'), name = 'redoc'),
    path('health/', health_check, name = 'health-check'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)